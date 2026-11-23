<template>
	<q-layout
		view="lHh Lpr lFf"
		id="page-small-casebook"
		@scroll="setHeaderBackground"
	>
		<q-header
			bordered
			:class="{
				'solid-bg': scrolled,
				'bg-transparent': !scrolled,
			}"
			class="text-black"
		>
			<q-toolbar class="text-h6 text-weight-bold">
				<q-btn
					flat
					dense
					round
					icon="navigate_before"
					aria-label="Back"
					:to="{ name: 'app.index' }"
				/>

				<div>病历本</div>
			</q-toolbar>
		</q-header>

		<q-page-container>
			<q-page padding>
				<q-card
					id="identification"
					class="q-my-sm"
					flat
				>
					<q-card-section
						class="q-px-sm q-py-xs"
						id="name"
					>
						<div class="text-h5 text-weight-bold">{{ fromProfileName }}</div>
					</q-card-section>

					<q-card-section
						class="q-px-sm q-py-xs"
						id="property"
					>
						{{ fromProfileGender }} | {{ fromProfileAge }}岁 | 泌尿科A区
					</q-card-section>

					<q-card-section
						class="q-px-sm q-py-xs"
						id="slot-code"
					>
						<div class="text-caption text-grey-6">
							<q-icon
								name="domain"
								class="q-mr-xs"
							/>住院号：38277466
						</div>
					</q-card-section>
				</q-card>

				<q-card
					flat
					id="profile"
					class="q-my-md overflow-hidden hidden"
				>
					<q-card-section class="q-pa-none">
						<q-btn
							label="体格检查"
							flat
							square
							class="text-weight-bold"
							id="profile-heading"
						></q-btn>
					</q-card-section>

					<q-card-section class="q-pa-none q-pa-sm">
						<div class="row q-col-gutter-xs">
							<profile-item
								class="col-3"
								v-for="(item, index) in profileList"
								:key="index"
								:label="item.label"
								:value="item.value"
							></profile-item>
						</div>
					</q-card-section>
				</q-card>

				<q-card
					id="detail"
					flat
					class="q-my-md"
				>
					<q-card-section class="q-pa-sm">
						<!-- <detail-item
							class="q-mb-sm"
							v-for="name in DETAIL_ITEM_LIST"
							:key="name"
							:label="details[name].label"
							:value="details[name].content"
						></detail-item> -->
						<detail-item
							class="q-mb-sm"
							label="主诉"
							:value="fromChiefComplaint"
						></detail-item>
						<detail-item
							class="q-mb-sm"
							label="现病史"
							:value="fromHistoryPresent"
						></detail-item>
						<detail-item
							class="q-mb-sm"
							label="既往史"
							:value="fromHistoryPast"
						></detail-item>
						<detail-item
							class="q-mb-sm"
							label="个人史"
							:value="fromHistoryIndividual"
						></detail-item>
						<detail-item
							class="q-mb-sm"
							label="婚姻史"
							:value="fromHistoryMarriage"
						></detail-item>
						<detail-item
							class="q-mb-sm"
							label="家族史"
							:value="fromHistoryFamily"
						></detail-item>
						<detail-item
							class="q-mb-sm"
							label="传染病史"
							:value="fromHistoryInfection"
						></detail-item>
						<detail-item
							class="q-mb-sm"
							label="预防接种史"
							:value="fromHistoryVaccination"
						></detail-item>
						<detail-item
							class="q-mb-sm"
							label="辅助检查"
							:value="fromHistoryExamination"
						></detail-item>
					</q-card-section>
				</q-card>
			</q-page>
		</q-page-container>
	</q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { QLayoutProps } from 'quasar';

import ProfileItem from './ProfileItem.vue';
import DetailItem from './DetailItem.vue';

import profileList from './sample/profile.json';

const scrolled = ref(false);

const setHeaderBackground: QLayoutProps['onScroll'] = (info) => {
	scrolled.value = info.position > 20;
};

import { Casebook, CasebookData } from 'src/model/Casebook';

const data = ref<CasebookData>({
	chiefComplaint: null,
	profile: {
		name: null,
		age: null,
		gender: 0,
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
});

const fromProfileGender = computed<string>(() => {
	const { gender } = data.value.profile;

	if (gender === 0) {
		return '未知';
	}

	if (gender === 1) {
		return '男性';
	}

	if (gender === 2) {
		return '女性';
	}

	throw new Error('Bad input value.');
});

const fromProfileName = computed<string>(() => {
	const { name } = data.value.profile;

	return name === null ? '未知' : name;
});

const fromProfileAge = computed<string>(() => {
	const { age } = data.value.profile;

	return age === null ? '-' : String(age);
});

const fromChiefComplaint = computed<string>(() => {
	const { chiefComplaint } = data.value;

	return chiefComplaint === null ? '不详' : chiefComplaint;
});

const fromHistoryPresent = computed<string>(() => {
	const { present } = data.value.history;

	return present === null ? '不详' : present;
});

const fromHistoryPast = computed<string>(() => {
	const { past } = data.value.history;

	return past === null ? '不详' : past;
});

const fromHistoryIndividual = computed<string>(() => {
	const { individual } = data.value.history;

	return individual === null ? '不详' : individual;
});

const fromHistoryMarriage = computed<string>(() => {
	const { marriage } = data.value.history;

	return marriage === null ? '不详' : marriage;
});

const fromHistoryFamily = computed<string>(() => {
	const { family } = data.value.history;

	return family === null ? '不详' : family;
});

const fromHistoryInfection = computed<string>(() => {
	const { infection } = data.value.history;

	return infection === null ? '不详' : infection;
});

const fromHistoryVaccination = computed<string>(() => {
	const { vaccination } = data.value.history;

	return vaccination === null ? '不详' : vaccination;
});

const fromHistoryExamination = computed<string>(() => {
	const { examination } = data.value.history;

	return examination === null ? '不详' : examination;
});

import { FetchCasebookData } from 'src/adaptor/FetchCasebookData';

onMounted(async function requestCasebookData() {
	const casebook = new Casebook();

	await FetchCasebookData(casebook);

	data.value = casebook.data;
});

defineOptions({ name: 'Page.SmallCasebook' });
</script>

<style lang="scss">
#page-small-casebook {
	background-color: #f4f5fa;

	.solid-bg {
		background-color: #f4f5fa;
	}

	.text-h6 {
		font-size: 16px;
	}

	&::before {
		content: '';
		display: block;
		position: absolute;
		top: 0;
		width: 100%;
		height: 210px;
		background: linear-gradient(51.58deg, #ffffff 0%, #d2efff 100%);
	}

	#identification {
		background-color: transparent;

		&::after {
			content: '';
			position: absolute;
			width: 150px;
			height: 200px;
			top: 16px;
			right: 10px;
			background-image: url('./image//icon-casebook.png');
			background-repeat: no-repeat;
			background-size: 100%;
		}
	}

	#profile {
		background-color: rgba(255, 255, 255, 0.8);

		#profile-heading {
			background: linear-gradient(
				180deg,
				#cae2eb 0%,
				rgba(202, 226, 235, 0) 100%
			);

			border-bottom-right-radius: $generic-border-radius;
		}
	}

	#detail {
		background: linear-gradient(
			180deg,
			#cae2eb 0%,
			rgba(202, 226, 235, 0) 100%
		);
	}
}
</style>
