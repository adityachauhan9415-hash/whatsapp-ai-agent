// whatsapp/index.js

const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason
} = require('@whiskeysockets/baileys');
const pino = require('pino');
const qrcode = require('qrcode-terminal');
const path = require('path');
const { spawn } = require('child_process');

console.log("Baileys bridge starting...")

let reconnectAttempts = 0;
const maxReconnectAttempts = 10;

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
            const statusCode = lastDisconnect.error?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
            const currentAttempt = reconnectAttempts + 1;
            const delay = Math.min(5000 * currentAttempt, 30000);

            console.log(`WhatsApp disconnected (attempt ${currentAttempt}/${maxReconnectAttempts}):`, statusCode || "Unknown reason");

            if (shouldReconnect && reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts++;
                console.log(`Attempting to reconnect in ${delay / 1000}s...`);
                setTimeout(() => {
                    connectToWhatsApp().catch(err => {
                        console.error("Fatal reconnection error:", err);
                        process.exit(1);
                    });
                }, delay);
            } else if (!shouldReconnect) {
                console.log("Logged out. Please delete auth_info_baileys and restart.");
                process.exit(0);
            } else {
                console.error("Max reconnection attempts reached.");
                process.exit(1);
            }
        } else if (connection === 'open') {
            reconnectAttempts = 0;
            console.log('WhatsApp connected');
        }
    });

    socket.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];

        // Ignore self messages, groups, status updates, and messages without text
        if (!msg.message || msg.key.fromMe || msg.key.remoteJid.includes('@g.us') || msg.key.remoteJid === 'status@broadcast') {
            return;
        }

        const sender = msg.key.remoteJid;
        const text = msg.message.conversation || msg.message.extendedTextMessage?.text;

        if (text) {
            console.log(`Incoming message from ${sender}: ${text}`);

            // Process message through Python pipeline
            const scriptPath = path.join(__dirname, '../src/bridge_cli.py');
            const pythonProcess = spawn('python', [scriptPath]);

            const inputData = {
                sender: sender,
                message: text
            };

            pythonProcess.stdin.write(JSON.stringify(inputData));
            pythonProcess.stdin.end();

            let stdoutData = '';
            pythonProcess.stdout.on('data', (data) => {
                stdoutData += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                console.error(`Python error output: ${data.toString()}`);
            });

            pythonProcess.on('close', async (code) => {
                if (code !== 0) {
                    console.error(`Python bridge exited with code ${code}`);
                    return;
                }

                try {
                    const result = JSON.parse(stdoutData);
                    console.log(`Pipeline result for ${sender}:`, JSON.stringify(result));

                    if (result.status === 'replied') {
                        const delayMs = result.delay_seconds * 1000;
                        await new Promise(resolve => setTimeout(resolve, delayMs));
                        await socket.sendMessage(sender, { text: result.reply });
                        console.log(`Reply sent to ${sender}: "${result.reply}"`);
                    } else if (result.status === 'manual_review_required') {
                        console.log(`Manual review flagged for ${sender}`);
                    }
                } catch (err) {
                    console.error('Error parsing Python output:', err);
                    console.error('Raw Python output:', stdoutData);
                }
            });
        }
    });
}

connectToWhatsApp().catch((err) => {
    console.error("Fatal initialization error:", err);
    process.exit(1);
});