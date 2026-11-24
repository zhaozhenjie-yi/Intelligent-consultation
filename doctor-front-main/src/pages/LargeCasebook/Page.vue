<template>
	<q-layout
		view="lHh Lpr lFf"
		id="page-large-casebook"
		class="bg-grey-3"
	>
		<q-page-container class="row justify-center">
			<q-page
				class="col col-xl-4 col-lg-6 col-md-7 col-sm-12 bg-white q-py-xl q-px-xl"
				style="min-width: 720px; max-width: 840px"
				padding
			>
				<q-banner v-if="loading">正在读取病历……</q-banner>
				<q-banner v-else-if="loadError" class="bg-red-1">{{ loadError }}<q-btn flat label="重试" @click="loadCasebook" /></q-banner>
				<q-btn v-else label="下载完整病历" :href="downloadUrl" />
				<div
					id="heading"
					class="flex justify-between q-pb-md"
				>
					<div
						class="text-h5"
						id="title"
					>
						<div>天津医科大学第二医院</div>
						<div class="text-caption text-uppercase text-weight-regular">
							THE SECOND HOSPITAL OF TIANJIN MEDICAL UNIVERSITY
						</div>
					</div>
					<div
						class="text-h5 text-right"
						id="category"
					>
						<div>入院记录</div>
						<div class="text-caption text-uppercase text-weight-regular">
							Admission record
						</div>
					</div>
				</div>

				<div
					id="location"
					class="flex justify-between q-pb-md q-mt-md"
				>
					<div id="room">
						<span class="text-grey-6">科室：</span>{{ casebook.class }}
					</div>
					<div id="code">
						<span class="text-grey-6">病历号：</span>{{ casebook.code }}
					</div>
				</div>

				<div class="row q-col-gutter-sm">
					<div class="col">
						<q-input readonly
							class="compact-form-input"
							outlined
							dense
							label="姓名"
							:model-value="casebook.profile.name"
						></q-input>
					</div>
					<div class="col">
						<q-input readonly
							class="compact-form-input"
							outlined
							dense
							label="性别"
							:model-value="casebook.profile.sex"
						></q-input>
					</div>
					<div class="col">
						<q-input readonly
							class="compact-form-input"
							outlined
							dense
							label="年龄"
							:model-value="casebook.profile.age"
						></q-input>
					</div>
				</div>

				<div class="row q-col-gutter-sm q-mt-sm">
					<div class="col">
						<q-input readonly
							class="classical-form-input"
							dense
							label="民族"
							:model-value="casebook.profile.family"
						></q-input>
					</div>
					<div class="col">
						<q-input readonly
							class="classical-form-input"
							dense
							label="婚姻状况"
							:model-value="casebook.profile.marriage"
						></q-input>
					</div>
					<div class="col">
						<q-input readonly
							class="classical-form-input"
							dense
							label="籍贯"
							:model-value="casebook.profile.registry"
						></q-input>
					</div>
					<div class="col">
						<q-input readonly
							class="classical-form-input"
							dense
							label="电话"
							:model-value="casebook.profile.phone"
						></q-input>
					</div>
					<div class="col">
						<q-input readonly
							class="classical-form-input"
							dense
							label="可靠程度"
							:model-value="String(casebook.profile.reliable)"
						></q-input>
					</div>
				</div>

				<div class="row q-col-gutter-sm q-mt-sm">
					<div class="col">
						<q-input readonly
							class="classical-form-input"
							stack-label
							dense
							label="职业"
							:model-value="casebook.profile.job"
							placeholder="无"
						></q-input>
					</div>
					<div class="col">
						<q-input readonly
							class="classical-form-input"
							stack-label
							dense
							label="工作单位"
							:model-value="casebook.profile.employer"
							placeholder="无"
						></q-input>
					</div>
				</div>

				<div class="row q-col-gutter-sm q-mt-sm">
					<div class="col">
						<q-input readonly
							class="classical-form-input"
							dense
							label="住址"
							:model-value="casebook.profile.address"
						></q-input>
					</div>
				</div>

				<div class="row q-col-gutter-sm q-mt-sm">
					<div class="col">
						<q-input readonly
							class="classical-form-input"
							dense
							label="入院日期"
							:model-value="toLocalString(casebook.profile.createdAt)"
						></q-input>
					</div>
					<div class="col">
						<q-input readonly
							class="classical-form-input"
							dense
							label="病历采写日期"
							:model-value="toLocalString(casebook.profile.recordedAt)"
						></q-input>
					</div>
				</div>

				<div
					id="signature"
					class="row q-col-gutter-sm q-mt-sm"
				>
					<div class="col">
						<q-input
							class="classical-form-input"
							dense
							readonly
							label="病史陈述者及签字"
							:model-value="null"
						></q-input>
					</div>
				</div>

				<q-input readonly autogrow type="textarea" outlined
					name="issue"
					class="q-mt-lg"
					label="患者主诉："
					:model-value="casebook.symptom.issue"
				/>

				<q-input readonly autogrow type="textarea" outlined
					name="current"
					class="q-mt-sm"
					label="现病史："
					:model-value="casebook.symptom.current"
				/>

				<q-input readonly autogrow type="textarea" outlined
					name="history"
					class="q-mt-sm"
					label="既往史："
					:model-value="casebook.symptom.history"
				/>

				<div class="row symptom-item q-pa-sm q-mt-sm">
					<div class="col-2 text-weight-bold">
						<div>体格检查：</div>

					</div>

					<div class="col row q-col-gutter-sm">
						<index-item
							class="col-3"
							v-for="item in INDEX_LIST"
							:key="item.name"
							:label="item.label"
							:value="String(indexes[item.name])"
						/>
					</div>
				</div>
			</q-page>
		</q-page-container>
	</q-layout>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue';
import { date } from 'quasar';
import IndexItem from './IndexItem.vue';
import { Casebook } from 'src/model/Casebook';
import { FetchCasebookData } from 'src/adaptor/FetchCasebookData';
import { getUserId } from 'src/adaptor/User';
import { errorMessage, API_BASE_URL } from 'src/adaptor/Api';

const uid = getUserId();
const loading = ref(true);
const loadError = ref('');
const downloadUrl = `${API_BASE_URL}/download_report?uid=${encodeURIComponent(uid)}`;
const casebook = reactive({
	class: '泌尿外科', code: '未登记',
	profile: { name: '', sex: '', age: '', family: '不详', marriage: '不详', registry: '不详', phone: '不详', reliable: '不详', job: '不详', employer: '不详', address: '不详', createdAt: '', recordedAt: '' },
	symptom: { issue: '', current: '', history: '' },
});
const INDEX_LIST = [{ name: 'heat', label: '体温（℃）' }, { name: 'pulse', label: '心率（次/分）' }, { name: 'breathe', label: '呼吸（次/分）' }, { name: 'pressure', label: '血压（mmHg）' }];
const indexes: Record<string, string> = { heat: '未提供', pulse: '未提供', breathe: '未提供', pressure: '未提供' };
function toLocalString(value: string) { return value ? date.formatDate(value, 'YYYY-MM-DD HH:mm') : '不详'; }
async function loadCasebook() {
	loading.value = true; loadError.value = '';
	try {
		const model = new Casebook();
		const patient = await FetchCasebookData(model);
		casebook.code = patient.medical_record_number || '未登记';
		const data = model.data;
		Object.assign(casebook.profile, { name: data.profile.name || '不详', age: data.profile.age === null ? '不详' : `${data.profile.age}岁`, sex: ['', '男', '女'][data.profile.gender] || '不详' });
		Object.assign(casebook.symptom, { issue: data.chiefComplaint || '不详', current: data.history.present || '不详', history: data.history.past || '不详' });
	} catch (error) { loadError.value = errorMessage(error); }
	finally { loading.value = false; }
}
onMounted(loadCasebook);
defineOptions({ name: 'Page.LargeCasebook' });
</script>

<style lang="scss">
#page-large-casebook {
	#heading {
		color: $front-color;

		.text-caption {
			font-size: 14px;
		}

		border-bottom: solid $front-color 4px;
	}

	#location {
		color: $front-color;
	}

	#signature {
		input {
			height: 72px;
		}

		.q-field__control {
			height: 96px;

			$gap: 10px;

			.q-field__control-container {
				height: 72px;

				&::after {
					text-align: center;
					line-height: 48px;
					font-size: 24px;
					color: #bbb;
					content: '患者在此区域内签名';
					display: block;
					position: absolute;
					border-color: #ddd;
					border-style: dashed;
					border-width: 2px;
					border-radius: 4px;
					top: $gap;
					left: $gap;
					right: $gap;
					bottom: $gap;
				}
			}
		}
	}
}
</style>
