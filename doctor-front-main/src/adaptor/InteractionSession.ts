import { Notify } from 'quasar';
import type { Session } from 'src/pages/Interaction/Session';
import { api, post, errorMessage } from './Api';

export async function SpeechToText(audioBlob: Blob, setText: (text: string) => void) {
	const form = new FormData();
	form.append('audioFile', audioBlob, 'recording.webm');
	const data = await api<{ content: string }>('upload_audio', { method: 'POST', body: form });
	setText(data.content);
}

export async function OnSessionCreated(session: Session) {
	session.lock();
	try {
		const data = await api<{ conversation_history: { content: string; role: string }[] }>(`get_conversation_history?uid=${encodeURIComponent(session.uid)}`);
		if (!data.conversation_history.length) session.put(false, '医生', '', '您好！请问您的姓名是？');
		for (const message of data.conversation_history) {
			session.put(message.role === 'user', message.role === 'user' ? '就诊人' : '医生', '', message.content);
		}
	} catch (error) {
		Notify.create({ type: 'negative', message: errorMessage(error) });
	} finally {
		session.unlock();
	}
	session.addEventListener('sending', () => session.lock());
	session.addEventListener('sent', async () => {
		session.lock();
		const recorder = session.receive('医生');
		try {
			const result = await post<{ text: string }>('generate_response', { uid: session.uid, text: session.messages[session.messages.length - 1].text });
			recorder.setText(result.text);
		} catch (error) {
			recorder.setText(`发送失败：${errorMessage(error)}。请重新发送。`);
		} finally {
			recorder.setAudio(new Blob()).end();
			session.unlock();
		}
	});
}

export async function runSessionAction(session: Session, action: () => Promise<string>) {
	if (session.locking) return;
	session.lock();
	const recorder = session.receive('医生');
	try {
		recorder.setText(await action());
	} catch (error) {
		recorder.setText(errorMessage(error));
	} finally {
		recorder.setAudio(new Blob()).end();
		session.unlock();
	}
}
