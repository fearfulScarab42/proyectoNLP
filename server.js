const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const app = express();
const port = 3000;
let promptData = {};

//app.use(express.static('public'));
app.use(express.json());
app.use(express.static(path.resolve(__dirname+ '/client/build')));

app.get("/api", (req, res) => {
    res.json({ message: "Hola desde el sasdasdervidor!" });
  });

app.post('/send-prompt', (req, res) => {
    const { prompt, clientId } = req.body;
    promptData[clientId] = prompt;
    res.status(200).send('Prompt recibido'+promptData[clientId]+clientId);
});

app.get('/stream/:clientId', (req, res) => {
    const clientId = req.params.clientId;
    const prompt = promptData[clientId];

    if (!prompt) {
        res.status(400).send('Prompt no encontrado');
        return;
    }

    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.flushHeaders();

    const pythonProcess = spawn('python', ['pyna.py']);

    pythonProcess.stdin.write(JSON.stringify({ prompt }));
    pythonProcess.stdin.end();

    pythonProcess.stdout.on('data', (data) => {
        const lines = data.toString().split('\n').filter(line => line.trim() !== '');
        for (const line of lines) {
            const response = JSON.parse(line).response;
            res.write(`data: ${response}\n\n`);
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess.on('close', () => {
        res.end();
    });

    req.on('close', () => {
        pythonProcess.kill();
    });
});

// Todas las peticiones GET que no hayamos manejado en las líneas anteriores retornaran nuestro app React
app.get('*', (req, res) => {
    res.sendFile(path.resolve(__dirname+ '/client/build', 'index.html'));
  });

app.listen(port, () => {
    console.log(`Servidor corriendo en http://localhost:${port}/`);
});
