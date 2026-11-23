import type { Casebook } from 'src/model/Casebook';
import * as User from './User';

const base_url = 'http://127.0.0.1:8503/api/';
export async function FetchCasebookData(casebook: Casebook) {
	//// IMPLEMENTATION START ////
	// NO EXCEPTION !!!
	const reportResponse = await fetch(base_url + '/generate_report', {
		method: 'POST',
		mode: 'cors',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			uid: User.id,
		}),
	});

	if (!reportResponse.ok) {
		return;
	}

	const { report } = await reportResponse.json();

	const response = await fetch(base_url + '/change_medical_record', {
		method: 'POST',
		mode: 'cors',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			uid: User.id,
			text: report,
		}),
	});

	if (!response.ok) {
		return;
	}

	const data = await response.json();
	const content = JSON.parse(data.content);

	casebook.setProfileName(content.name);
	casebook.setProfileAge(content.age);
	casebook.setChiefComplaint(content.chief_complaint);
	casebook.setIndividualHistory(content.personal_history);
	casebook.setPastHistory(content.past_medical_history);
	casebook.setPresentHistory(content.history_of_present_illness);
	casebook.setMarriageHistory(content.marital_and_reproductive_history);
	casebook.setFamilyHistory(content.family_and_genetic_history);
	casebook.setInfectionHistory(content.history_of_infectious_diseases);
	casebook.setVaccinationHistory(content.vaccination_history);
	casebook.setExaminationHistory(content.auxiliary_inspection_records);

	const { gender } = content;

	if (gender === '男') {
		casebook.setProfileGenderAsMale();
	} else if (gender === '女') {
		casebook.setProfileGenderAsFemale();
	} else {
		casebook.setProfileGenderAsUnknown();
	}

	//// IMPLEMENTATION END ////
}
