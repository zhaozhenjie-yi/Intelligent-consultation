type TextSetter = (text: string) => void;

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const base_url = 'http://127.0.0.1:8503/api/';
export async function SpeechToText(audioBlob: Blob, setText: TextSetter) {
	// Assuming the Flask endpoint is '/upload_audio'
	const url = base_url + '/upload_audio';

	// Create a FormData object and append the audio blob
	const formData = new FormData();
	formData.append('audioFile', audioBlob, 'recording.webm');
	const headers = new Headers();
	headers.append('Access-Control-Allow-Origin', '*');
	try {
		// Make the POST request to the Flask server
		const response = await fetch(url, {
			method: 'POST',
			body: formData,
			headers: headers,
			credentials: 'include',
			// Headers are not needed for FormData; the browser sets the correct multipart/form-data boundary
		});

		// Check if the upload was successful
		if (response.ok) {
			const result = await response.json(); // Assuming the server responds with JSON
			const segments = [];

			for (const word of result.content) {
				const delay = Math.trunc(Math.random() * 200);

				await sleep(delay);
				segments.push(word);
				setText(segments.join(''));
			}
		} else {
			console.error('Upload failed', response.statusText);
			// Handle errors or unsuccessful upload
		}
	} catch (error) {
		console.error('Error during fetch', error);
		// Handle network errors
	}
}

import type { Session } from 'src/pages/Interaction/Session';
import * as User from './User';
import mock from './mock.json';
import conversation from './conversation.json';

interface ChatHistoryRecord {
	content: string;
	role: 'user' | 'assistant';
}

const AUDIO_URL_PADDING = 'http://example.com';

export async function OnSessionCreated(session: Session) {
	session.lock();

	for (const { sent, who, text } of mock) {
		session.put(sent, who, AUDIO_URL_PADDING, text);
	}

	const url = new URL(`${base_url}get_conversation_history`);

	url.searchParams.set('uid', User.id);

	await fetch(url, { method: 'GET', mode: 'cors' })
		.then(async (response) => {
			if (!response.ok) {
				throw new Error('Request conversation history failed');
			}

			const json = await response.json();

			return json.conversation_history as ChatHistoryRecord[];
		})
		.catch(() => conversation) // JUST FOR DEBUGING.
		.then((history) => {
			for (const { content, role } of history) {
				const subject: [boolean, string] = [false, 'bot'];

				if (role === 'user') {
					subject[0] = true;
					subject[1] = '就诊人';
				}

				session.put(...subject, AUDIO_URL_PADDING, content);
			}
		})
		.finally(() => session.unlock());

	session.addEventListener('sending', () => session.lock());

	session.addEventListener('sent', async function reply() {
		session.lock();

		const recorder = session.receive('bot');
		const url = base_url + '/generate_response'; // Replace with your actual Flask endpoint
		const data = {
			text: session.messages[session.messages.length - 1].text,
			uid: User.id,
		};

		try {
			const response = await fetch(url, {
				method: 'POST', // or 'PUT'
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(data), // convert data to JSON string
				credentials: 'include',
			});

			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}

			const responseData = await response.json(); // Parse JSON response
			const segments = [];
			console.log(responseData.text);
			for (const word of responseData.text) {
				const delay = Math.trunc(Math.random() * 200);

				await sleep(delay);
				segments.push(word);
				recorder.setText(segments.join(''));
				// 自动播放可以在这里实现成副作用
				// https://developer.mozilla.org/en-US/docs/Web/API/HTMLAudioElement
			}
			recorder.setAudio(new Blob());
			recorder.end();
		} catch (error) {
			console.error('Request failed:', error);
			// Handle errors here
		}

		session.unlock();
	});
}
