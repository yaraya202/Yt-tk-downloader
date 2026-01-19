import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execPromise = promisify(exec);

async function download() {
    const args = process.argv.slice(2);
    const url = args[0];
    const type = args[1]; // 'audio' or 'video'
    const outputPath = args[2];

    try {
        console.log(`Fetching data for URL: ${url} (Type: ${type})`);
        
        let command = '';
        if (type === 'audio') {
            command = `python3 -m yt_dlp -x --audio-format mp3 -o "${outputPath}" "${url}"`;
        } else {
            command = `python3 -m yt_dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "${outputPath}" "${url}"`;
        }

        console.log(`Executing: ${command}`);
        const { stdout, stderr } = await execPromise(command);
        
        if (stderr && !stderr.includes('Extracting') && !stderr.includes('Destination')) {
            console.error('yt-dlp stderr:', stderr);
        }
        
        console.log('Success');
        process.exit(0);

    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

download();
