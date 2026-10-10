console.log("Baileys bridge starting...")

const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason
} = require('@whiskeysockets/baileys');
const pino = require('pino');
const qrcode = require('qrcode-terminal');

console.log("Calling connectToWhatsApp...")

async function connectToWhatsApp() {
    console.log("Initializing auth state...")
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');

    const socket = makeWASocket({
        logger: pino({ level: 'silent' }),
        printQRInTerminal: true,
        auth: state
    });

    socket.ev.on('creds.update', saveCreds);

    socket.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        if (qr) {
            console.log("Scan this QR in WhatsApp > Linked Devices:");
            qrcode.generate(qr, { small: true });
        }
        if (connection === 'close') {
            let reconnectAttempts = 0;
        const maxReconnectAttempts = 10;

        const shouldReconnect = (lastDisconnect.error)?.output?.statusCode !== DisconnectReason.loggedOut;
        if (shouldReconnect && reconnectAttempts < maxReconnectAttempts) {
                console.log("Attempting to reconnect...");
                setTimeout(() => {
                    connectToWhatsApp().catch((err) => {
                        console.error("Fatal Baileys error:", err);
                        process.exit(1);
                    });
                }, 5000); // 5 second delay before reconnecting
            }
            reconnectAttempts++;
        console.log(`WhatsApp disconnected (attempt ${reconnectAttempts}/${maxReconnectAttempts}):`, lastDisconnect.error?.output?.statusCode || "Unknown reason");
        } else if (connection === 'open') {
            reconnectAttempts = 0;
            console.log('WhatsApp connected');
        }
    });

    socket.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];

        // Ignore self messages, groups, and status updates
        if (!msg.message || msg.key.fromMe || msg.key.remoteJid.includes('@g.us') || msg.key.remoteJid === 'status@broadcast') {
            return;
        }

        // Process message through Python pipeline
        const { spawn } = require('child_process');
        const path = require('path');
        const scriptPath = path.join(__dirname, '../src/bridge_cli.py');
        const pythonProcess = spawn('python', [scriptPath]);

        // Prepare input data
        const inputData = {
            sender: msg.key.remoteJid,
            message: msg.message.conversation || msg.message.extendedTextMessage?.text
        };

        // Send input to Python script
        pythonProcess.stdin.write(JSON.stringify(inputData));
        pythonProcess.stdin.end();

        // Handle Python script output
        pythonProcess.stdout.on('data', async (data) => {
            try {
                const result = JSON.parse(data.toString());
                console.log(`Pipeline result: ${JSON.stringify(result)}`);

                // Handle pipeline result
                if (result.status === 'replied') {
                    // Wait for delay
                    await new Promise(resolve => setTimeout(resolve, result.delay_seconds * 1000));

                    // Send reply
                    await socket.sendMessage(
                        msg.key.remoteJid,
                        { text: result.reply }
                    );
                    console.log(`Reply sent to ${msg.key.remoteJid}`);
                } else if (result.status === 'manual_review_required') {
                    console.log(`Manual review required for message from ${msg.key.remoteJid}`);
                }
            } catch (err) {
                console.error('Error processing pipeline result:', err);
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`Python error: ${data}`);
        });

        const sender = msg.key.remoteJid;
        const text = msg.message.conversation || msg.message.extendedTextMessage?.text;
        const timestamp = new Date(msg.messageTimestamp * 1000).toLocaleString();

        if (text) {
            console.log(`Sender: ${sender}`);
            console.log(`Text: ${text}`);
            console.log(`Timestamp: ${timestamp}`);
            console.log('---');
        }
    });
}

connectToWhatsApp().catch((err) => {
    console.error("Fatal Baileys error:", err);
    process.exit(1);
});
