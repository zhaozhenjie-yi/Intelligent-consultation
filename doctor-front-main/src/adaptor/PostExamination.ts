import type { Session } from 'src/pages/Interaction/Session';
import * as User from './User';

const base_url = 'http://127.0.0.1:8503/api/';
export async function PostExamination(session: Session, file: File) {
	const recorder = session.receive('bot');

	//// IMPLEMENTATION START ////
	// NO EXCEPTION !!!
	const formData = new FormData();

	formData.append('uid', User.id);
	formData.append('image', file);

	const response = await fetch(base_url + '/upload_check_record', {
		method: 'POST',
		mode: 'cors',
		body: formData,
		credentials: 'include',
	});

	if (response.ok) {
		const data = await response.json();

		recorder.setText('ok post');
		recorder.setText(data.ocr_result);
	} else {
		recorder.setText('<span style="color:red">failed.</span>');
	}
	//// IMPLEMENTATION END ////

	recorder.setAudio(new Blob());
	recorder.end();
}
