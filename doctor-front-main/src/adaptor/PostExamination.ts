import type { Session } from 'src/pages/Interaction/Session';
import { api } from './Api';
import { runSessionAction } from './InteractionSession';

export async function PostExamination(session: Session, file: File) {
	await runSessionAction(session, async () => {
		const form = new FormData();
		form.append('uid', session.uid);
		form.append('image', file);
		const result = await api<{ text: string }>('upload_check_record', { method: 'POST', body: form });
		return `检查报告已识别并保存：\n${result.text}`;
	});
}
