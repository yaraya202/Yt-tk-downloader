import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs';

const execPromise = promisify(exec);

const COOKIES = `__Secure-1PSIDTS=sidts-CjUB7I_69FxHW2QCiA4MxMN3cOdtRC92m5e79NG729hrvN-u7yf2XHnEUj6EMclRyCa2ny1AdBAA; __Secure-3PSIDTS=sidts-CjUB7I_69FxHW2QCiA4MxMN3cOdtRC92m5e79NG729hrvN-u7yf2XHnEUj6EMclRyCa2ny1AdBAA; HSID=Axvvi7FadBeeCoEkp; SSID=As1unpmenzygkSXVV; APISID=59zjzUgQktgx33dq/AAOi3y4BYyIC72S-6; SAPISID=LiKWq-8gQME3PYNf/A0xqExwiRrW7Gl1oi; __Secure-1PAPISID=LiKWq-8gQME3PYNf/A0xqExwiRrW7Gl1oi; __Secure-3PAPISID=LiKWq-8gQME3PYNf/A0xqExwiRrW7Gl1oi; SID=g.a0005wjQsplZsjkxOo5-mAeXeKE0W1wyrgl3mGjjVkRp9zcJQYLwl8a1NBOcm4e0OIHjQupXegACgYKAX0SARESFQHGX2MiNz_hpzfNW07XmFPfSEZJJxoVAUF8yKp-UkljsQgpIq__3lRC_6jH0076; __Secure-1PSID=g.a0005wjQsplZsjkxOo5-mAeXeKE0W1wyrgl3mGjjVkRp9zcJQYLwzgIGckwk68KATq2EJ93fqgACgYKAQwSARESFQHGX2MiouSgqy9S8yGfvSY5GTyDlBoVAUF8yKo77IK6heNTP55gviNrP4dC0076; __Secure-3PSID=g.a0005wjQsplZsjkxOo5-mAeXeKE0W1wyrgl3mGjjVkRp9zcJQYLwhnWLSc3DBpeVigBTfQ5HCgACgYKAV8SARESFQHGX2Miv0afKeDsv9PLSPy8dnoimhoVAUF8yKrhh4xLrzl_FfKuJhCAH1xK0076; __Secure-YNID=15.YT=VzqodTPSls3c8rbOYwmoHXYUq3V9lQjo5ipqIkk5A8rDsPkLQDGvVHRs7gmsZRl99CKkPpLIJMkBTi_9iEXjGOrN-3YcqwvOcRVfpvdyTpes69t-THuRf4Lg9WpG7VUbHVDQSoddQq4ilWb68mICAr849urd8UmB1A9PmOKfYf2pQ6iFjF64yhcYYGLAd4A2lb3OFCS1zeY4YKp3DSWNwYTnBpLb4KxM6IKKoz9-HVOUPigE0CHwnBr_4VNQupKHsIIsbkg3eaojpfUNNw8OpbipzKAGR78kaFMgeZ592OvpuJSF2NRfyHpTLSlxdpqkylkNwPgiJ876N_wQjFaWlA; YSC=NPJ_EOYiux4; VISITOR_INFO1_LIVE=7YzMqpAepms; VISITOR_PRIVACY_METADATA=CgJQSxIEGgAgZQ%3D%3D; PREF=f6=40000000&tz=Asia.Karachi; __Secure-ROLLOUT_TOKEN=CO3Ox7-pgp5wEIb97eull5IDGLjMneiyl5ID; SIDCC=AKEyXzWPrlZBPKS77oNwZqRp0MOT6bYrmketWOYSPs-8Y-GbBpRmtLYisbs9a-NvUWOlri8CEg; __Secure-1PSIDCC=AKEyXzUSUizLeWAOaCjXu0Xbul72VnA9ins55qofiVQArOb2ZKM4IL03qwQIIV5f3tz-U2J88w; __Secure-3PSIDCC=AKEyXzUVF8x5Wtulgmgwj4jXkNrCoGlquYHagIwXCLvanwfzchwUxQzRzZVWjHjuZuUmtBjm`;

async function download() {
    const args = process.argv.slice(2);
    const url = args[0];
    const type = args[1]; // 'audio' or 'video'
    const outputPath = args[2];

    try {
        console.log(`Fetching data for URL: ${url} (Type: ${type})`);
        
        // Get title first
        const titleResult = await execPromise(`python3 -m yt_dlp --add-header "Cookie:${COOKIES}" --get-title --no-playlist "${url}"`);
        const title = titleResult.stdout.trim().replace(/[^\w\s-]/g, '');
        console.log(`TITLE_START|${title}|TITLE_END`);

        let command = '';
        if (type === 'audio') {
            command = `python3 -m yt_dlp --add-header "Cookie:${COOKIES}" --no-playlist --no-check-certificate -x --audio-format mp3 -o "${outputPath}" "${url}"`;
        } else {
            command = `python3 -m yt_dlp --add-header "Cookie:${COOKIES}" --no-playlist --no-check-certificate -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "${outputPath}" "${url}"`;
        }

        console.log(`Executing: ${command}`);
        const { stdout, stderr } = await execPromise(command);
        
        console.log('Success');
        process.exit(0);

    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

download();
