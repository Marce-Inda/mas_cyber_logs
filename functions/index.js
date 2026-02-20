const { onRequest } = require("firebase-functions/v2/https");
const admin = require("firebase-admin");
const logger = require("firebase-functions/logger");

admin.initializeApp();

exports.generateLogs = onRequest(async (req, res) => {
    // Permite recibir los logs desde el script MAS y guardarlos en Storage
    if (req.method !== "POST") {
        return res.status(405).send("Method Not Allowed");
    }

    try {
        const logs = req.body;
        if (!logs || !Array.isArray(logs)) {
            return res.status(400).send("Invalid logs array");
        }

        const bucketName = "the-responder-36ce2.appspot.com";
        const bucket = admin.storage().bucket(bucketName);

        const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
        const filename = `mas-logs/logs_${timestamp}.json`;
        const file = bucket.file(filename);

        const logsStr = JSON.stringify(logs, null, 2);
        await file.save(logsStr, {
            contentType: "application/json",
        });

        logger.info(`Saved ${logs.length} logs to ${filename}`);
        res.status(200).send({
            success: true,
            message: `Logs saved successfully to ${filename}`,
            file: filename
        });
    } catch (error) {
        logger.error("Error saving logs:", error);
        res.status(500).send("Internal Server Error");
    }
});
