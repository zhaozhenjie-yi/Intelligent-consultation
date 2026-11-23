type StringOrNull = string | null;

export interface CasebookHistoryData {
	present: StringOrNull;
	past: StringOrNull;
	individual: StringOrNull;
	marriage: StringOrNull;
	family: StringOrNull;
	infection: StringOrNull;
	vaccination: StringOrNull;
	examination: StringOrNull;
}

export interface CasebookProfileData {
	name: string | null;
	gender: 0 | 1 | 2;
	age: number | null;
}

export interface CasebookData {
	chiefComplaint: string | null;
	profile: CasebookProfileData;
	history: CasebookHistoryData;
}

function assertStringOrNull(value: unknown) {
	if (value !== null && typeof value !== 'string') {
		throw new TypeError('Invalid "value", one "null or string" expected.');
	}
}

export class Casebook {
	#data: CasebookData = {
		chiefComplaint: null,
		profile: {
			name: null,
			gender: 0,
			age: null,
		},
		history: {
			present: null,
			past: null,
			individual: null,
			marriage: null,
			family: null,
			infection: null,
			vaccination: null,
			examination: null,
		},
	};

	setProfileName(value: StringOrNull = null) {
		assertStringOrNull(value);
		this.#data.profile.name = value;

		return this;
	}

	setProfileGenderAsMale() {
		this.#data.profile.gender = 1;

		return this;
	}

	setProfileGenderAsFemale() {
		this.#data.profile.gender = 2;

		return this;
	}

	setProfileGenderAsUnknown() {
		this.#data.profile.gender = 0;

		return this;
	}

	setProfileAge(value: CasebookProfileData['age'] = null) {
		if (value !== null && !(Number.isInteger(value) && value >= 0)) {
			throw new TypeError(
				'Invalid "value", one "null or integer >= 0" expected.',
			);
		}

		this.#data.profile.age = value;

		return this;
	}

	setChiefComplaint(value: StringOrNull = null) {
		assertStringOrNull(value);
		this.#data.chiefComplaint = value;

		return this;
	}

	setPresentHistory(value: StringOrNull = null) {
		assertStringOrNull(value);
		this.#data.history.present = value;

		return this;
	}

	setPastHistory(value: StringOrNull = null) {
		assertStringOrNull(value);
		this.#data.history.past = value;

		return this;
	}

	setIndividualHistory(value: StringOrNull = null) {
		assertStringOrNull(value);
		this.#data.history.individual = value;

		return this;
	}

	setMarriageHistory(value: StringOrNull = null) {
		assertStringOrNull(value);
		this.#data.history.marriage = value;

		return this;
	}

	setFamilyHistory(value: StringOrNull = null) {
		assertStringOrNull(value);
		this.#data.history.family = value;

		return this;
	}

	setInfectionHistory(value: StringOrNull = null) {
		assertStringOrNull(value);
		this.#data.history.infection = value;

		return this;
	}

	setVaccinationHistory(value: StringOrNull = null) {
		assertStringOrNull(value);
		this.#data.history.vaccination = value;

		return this;
	}

	setExaminationHistory(value: StringOrNull = null) {
		assertStringOrNull(value);
		this.#data.history.examination = value;

		return this;
	}

	get data() {
		return {
			...this.#data,
			profile: { ...this.#data.profile },
			history: { ...this.#data.history },
		};
	}
}
