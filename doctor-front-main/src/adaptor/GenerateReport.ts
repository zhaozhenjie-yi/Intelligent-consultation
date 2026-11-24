import type { Session } from 'src/pages/Interaction/Session';
import { post } from './Api';
import { runSessionAction } from './InteractionSession';

export async function GenerateReport(session: Session) {
	await runSessionAction(session, async () => {
		const data = await post<{ report: string }>('generate_report', { uid: session.uid });
		return data.report;
	});
}
