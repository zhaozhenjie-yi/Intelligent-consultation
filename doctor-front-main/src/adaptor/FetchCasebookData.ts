import type { Casebook } from 'src/model/Casebook';
import { getUserId } from './User';
import { post } from './Api';

export async function FetchCasebookData(casebook: Casebook) {
	const uid = getUserId();
	const { report } = await post<{ report: string }>('generate_report', { uid });
	const data = await post<{ content: string; patient: { name?: string; age?: number | null; gender?: string; medical_record_number?: string } }>('change_medical_record', { uid, text: report });
	const content = JSON.parse(data.content);
	const text = (key: string) => typeof content[key] === 'string' ? content[key] : null;
	casebook.setProfileName(data.patient.name || text('name'));
	casebook.setProfileAge(data.patient.age ?? (Number.isInteger(content.age) && content.age >= 0 ? content.age : null));
	casebook.setChiefComplaint(text('chief_complaint'));
	casebook.setIndividualHistory(text('personal_history'));
	casebook.setPastHistory(text('past_medical_history'));
	casebook.setPresentHistory(text('history_of_present_illness'));
	casebook.setMarriageHistory(text('marital_and_reproductive_history'));
	casebook.setFamilyHistory(text('family_and_genetic_history'));
	casebook.setInfectionHistory(text('history_of_infectious_diseases'));
	casebook.setVaccinationHistory(text('vaccination_history'));
	casebook.setExaminationHistory(text('auxiliary_inspection_records'));
	const gender = ['男', '女'].includes(data.patient.gender || '') ? data.patient.gender : content.gender;
	if (gender === '男') casebook.setProfileGenderAsMale();
	else if (gender === '女') casebook.setProfileGenderAsFemale();
	else casebook.setProfileGenderAsUnknown();
	return data.patient;
}
