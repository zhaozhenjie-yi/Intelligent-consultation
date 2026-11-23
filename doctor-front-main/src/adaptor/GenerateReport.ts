import type { Session } from 'src/pages/Interaction/Session';
import * as User from './User';

const base_url = 'http://127.0.0.1:8503/api/';
export async function GenerateReport(session: Session) {
	const recorder = session.receive('bot');

	//// IMPLEMENTATION START ////
	// NO EXCEPTION !!!
	const response = await fetch(base_url + '/generate_report', {
		method: 'POST',
		mode: 'cors',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			uid: User.id,
		}),
	});

	if (response.ok) {
		const data = await response.json();

		recorder.setText('ok post');
		recorder.setText(data.report);
	} else {
		// <br> to break line in HTML instead of "\n"
		recorder.setText('<span style="color:red">fai<br>led.</span>');
	}
	//// IMPLEMENTATION END ////

	recorder.setAudio(new Blob());
	recorder.end();
}
