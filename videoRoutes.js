// routes/videoRoutes.js
const express = require('express');
const { exec } = require('child_process'); // Import exec to run commands
const router = express.Router();

router.post('/generate', (req, res) => {
    const prompt = req.body.prompt; // Assuming you're sending a JSON body with a 'prompt' field
    
    // Command to run the Python script
    const command = `python3 /Users/bhatsakib/Desktop/TXT_VID/services/videoService.py "${prompt}"`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            return res.status(500).json({ message: "Video generation failed", error: error.message });
        }
        console.log(stdout); // Log the output of the Python script
        res.status(200).json({ message: "Video generated successfully", output: stdout });
    });
});

module.exports = router;
