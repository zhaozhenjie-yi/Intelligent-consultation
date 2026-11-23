<template>
	<q-layout
		view="hHh lpR fFf"
		id="page-interaction"
		class="non-selectable"
	>
		<q-header
			bordered
			class="text-black"
		>
			<q-toolbar>
				<q-btn
					flat
					dense
					round
					icon="arrow_back"
					aria-label="返回首页"
					:to="{ name: 'app.index' }"
					class="q-mr-sm"
				/>
				
				<q-toolbar-title>
					<div
						class="text-h6 text-weight-bold"
						style="line-height: 20px"
					>
						海河优医
					</div>
					<div class="text-caption text-grey-6">
						<q-icon
							class="icon-align-fix text-positive q-mr-xs"
							name="fiber_manual_record"
						/>
						已接入智能助手
					</div>
				</q-toolbar-title>
				
				<div v-if="patientInfo" class="q-ml-md text-subtitle1">
					<q-chip color="primary" text-color="white">
						就诊人：{{ patientInfo.name || '未知' }} (UID: {{ patientInfo.uid || '未知' }})
					</q-chip>
				</div>
				
				<q-btn-dropdown
					flat
					split
					disable-main-btn
					dropdown-icon="menu"
					content-style="box-shadow: 0px 8px 20px 0px #0000001A;"
				>
					<q-list separator>
						<q-item
							clickable
							@click="requestFileBrowser"
							v-close-popup
						>
							<q-item-section side>
								<q-icon
									class="text-black"
									name="backup"
								/>
							</q-item-section>
							<q-item-section>
								<q-item-label>上传检查报告</q-item-label>
							</q-item-section>
						</q-item>

						<q-item
							clickable
							:to="{ name: 'app.small.casebook' }"
						>
							<q-item-section side>
								<q-icon
									class="text-black"
									name="folder_open"
								/>
							</q-item-section>
							<q-item-section>
								<q-item-label>查看病例本</q-item-label>
							</q-item-section>
						</q-item>

						<q-item
							clickable
							v-close-popup
							@click="generateReport"
						>
							<q-item-section side>
								<q-icon
									class="text-black"
									name="file_download"
								/>
							</q-item-section>
							<q-item-section>
								<q-item-label>生成病例</q-item-label>
							</q-item-section>
						</q-item>
					</q-list>
				</q-btn-dropdown>
			</q-toolbar>
		</q-header>

		<q-page-container>
			<input
				type="file"
				ref="browser"
				class="invisible fixed"
				@change="uploadExamination"
			/>
			<q-page
				padding
				class="q-pa-md"
			>
				<template
					v-for="(message, index) in messages"
					:key="index"
				>
					<q-chat-message
						class="q-mt-md q-mb-xs"
						:text="[message.text]"
						:bg-color="message.sent ? 'grey-4' : 'white'"
						:name="message.who"
						:sent="message.sent"
						text-html
						@click="playOrPause(message.audioURL)"
					>
						<template
							v-if="!message.sent"
							v-slot:name
						>
							<q-avatar
								class="q-mb-xs"
								size="32px"
								><img src="/ai.jpg"
							/></q-avatar>
						</template>

						<template
							v-if="index === 0"
							v-slot:stamp
						>
							<div class="text-grey-8">
								<q-icon
									class="icon-align-fix q-mr-xs q-mt-xs"
									name="help_outline"
								/>
								使用帮助请点击右上角
							</div>
						</template>
					</q-chat-message>
				</template>

				<q-chat-message
					class="q-mt-md q-mb-xs"
					:text="[inputingText]"
					bg-color="grey-4"
					:name="patientInfo?.name || '就诊人'"
					sent
					text-html
					stamp="正在分析您的语音..."
					v-if="inputing !== null"
				></q-chat-message>

				<q-chat-message
					class="q-mt-md q-mb-xs"
					:text="[receivingText]"
					bg-color="white"
					text-html
					v-if="receiving !== null"
				>
					<template v-slot:name>
						<q-avatar
							class="q-mb-xs"
							size="32px"
							><img src="/ai.jpg"
						/></q-avatar>
					</template>
				</q-chat-message>
				<div ref="bottom"></div>
			</q-page>
		</q-page-container>

		<q-footer
			bordered
			class="no-border"
		>
			<q-toolbar class="row">
				<!-- 输入框和发送按钮 -->
				<q-input
					v-model="textInput"
					placeholder="请输入文字"
					dense
					outlined
					square
					class="col-grow q-mr-sm"
				/>
				<q-btn
					flat
					class="text-black text-h6"
					style="line-height: 50px"
					icon="send"
					label="发送"
					@click="sendText"
					dense
				/>
			</q-toolbar>
			<q-toolbar class="q-pa-none hidden">
				<q-btn
					@contextmenu.prevent
					@touchstart.stop="startInput"
					@touchend.stop="appendMessage"
					flat
					class="full-width text-black text-h6"
					style="line-height: 50px"
					:class="{ gradient: inputing !== null }"
					:icon="inputing !== null ? 'radio_button_checked' : 'mic'"
					:label="inputing !== null ? '说话中...' : '点击后开始说话'"
					v-if="!locking"
				/>
				<q-btn
					@contextmenu.prevent
					disable
					flat
					class="full-width text-black text-h6"
					style="line-height: 50px"
					icon="pending"
					label="正在分析..."
					v-if="locking"
				/>
			</q-toolbar>
		</q-footer>
		<audio
			ref="player"
			class="invisible"
			:src="playing"
		></audio>
	</q-layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { scroll, useQuasar } from 'quasar';
import { useRoute } from 'vue-router';
import { Session, Recorder, RecorderEvent } from './Session';

// 定义props
const props = defineProps<{
	uid?: string
}>();

interface Message {
	sent: boolean;
	who: string;
	text: string;
	audioURL: string;
}

interface PatientInfo {
	uid: string;
	name?: string;
}

const messages: Message[] = reactive([]);
const bottom = ref<HTMLDivElement>(document.createElement('div'));
const browser = ref<HTMLInputElement>(document.createElement('input'));
const inputing = ref<Recorder | null>(null);
const inputingText = ref<string>('');
const receiving = ref<Recorder | null>(null);
const receivingText = ref<string>('');
const locking = ref(false);
const playing = ref<string>('');
const player = ref<HTMLAudioElement>(document.createElement('audio'));
// 文本输入框
const textInput = ref('');
// 患者信息
const patientInfo = ref<PatientInfo | null>(null);
const route = useRoute();
const $q = useQuasar();

// 解析URL中的uid参数
onMounted(() => {
	parseUrlForUid();
	
	// 添加hashchange监听，以便在hash变化时重新解析UID
	window.addEventListener('hashchange', parseUrlForUid);
});

// 在组件卸载时移除事件监听
onUnmounted(() => {
	window.removeEventListener('hashchange', parseUrlForUid);
});

// 从URL中解析UID的函数
function parseUrlForUid() {
	// 优先从查询参数获取UID
	let uid = route.query.uid as string;
	
	// 如果没有，尝试从props或路由参数获取
	if (!uid) {
		uid = props.uid || route.params.uid as string;
	}
	
	if (uid) {
		patientInfo.value = { uid };
		// 从localStorage获取患者信息
		try {
			const savedPatients = localStorage.getItem('patientData');
			if (savedPatients) {
				const patients = JSON.parse(savedPatients);
				const patient = patients.find((p: { uid: string }) => p.uid === uid);
				if (patient) {
					patientInfo.value = {
						uid,
						name: patient.name,
					};
					
					// 更新患者的问诊状态
					patient.consulted = true;
					patient.consultationCount += 1;
					localStorage.setItem('patientData', JSON.stringify(patients));
				}
			}
		} catch (e) {
			console.error('Failed to parse patient data', e);
		}
	} else if ($q && typeof $q.notify === 'function') {
		// 只在$q可用且notify函数存在时才调用
		$q.notify({
			color: 'warning',
			message: '未识别到就诊人信息',
			icon: 'warning',
		});
	} else {
		console.warn('未识别到就诊人信息');
	}
}

async function playOrPause(audioURL: string) {
	playing.value = audioURL;

	const { value: audio } = player;

	audio.load();

	if (audio.readyState !== 4) {
		await new Promise((resolve) => audio.addEventListener('canplay', resolve));
	}

	audio.play();
}

function scrollToBottom(duration: number = 0) {
	scroll.setVerticalScrollPosition(window, bottom.value.offsetTop, duration);
}

const session = new Session();

function render() {
	messages.splice(0);

	messages.push(
		...session.messages.map((message) => {
			return {
				sent: message.sent,
				who: message.who,
				text: message.text,
				audioURL: message.audioURL,
			};
		}),
	);
}

render();
session.addEventListener('push-message', render);

session.addEventListener('lock-change', () => {
	locking.value = session.locking;
	scrollToBottom();
});

session.addEventListener('receiving', (event) => {
	const recorderEvent = event as RecorderEvent;
	const recorder = recorderEvent.recorder as Recorder;

	receiving.value = recorder;

	recorder.addEventListener('text-change', () => {
		receivingText.value = recorder.text as string;
		scrollToBottom();
	});
});

session.addEventListener('received', () => {
	receiving.value = null;
	receivingText.value = '';
});

async function startInput() {
	const recorder = session.sent(patientInfo.value?.name || '就诊人');

	recorder.addEventListener('text-change', () => {
		inputingText.value = recorder.text as string;
		scrollToBottom();
	});

	inputingText.value = ' ';
	inputing.value = recorder;
	await recorder.start();
}

async function appendMessage() {
	const { value: recorder } = inputing;

	if (recorder === null) {
		return;
	}

	await recorder.stop(true);
	inputing.value = null;
	scrollToBottom(500);
}

async function sendText() {
	if (!textInput.value.trim()) {
		return;
	}
	
	session.put(true, patientInfo.value?.name || '就诊人', 'example', textInput.value);
	
	// 如果有就诊人ID，更新问诊状态
	if (patientInfo.value?.uid) {
		try {
			const savedPatients = localStorage.getItem('patientData');
			if (savedPatients) {
				const patients = JSON.parse(savedPatients);
				const patientIndex = patients.findIndex((p: { uid: string }) => p.uid === patientInfo.value?.uid);
				if (patientIndex !== -1) {
					patients[patientIndex].consulted = true;
					localStorage.setItem('patientData', JSON.stringify(patients));
				}
			}
		} catch (e) {
			console.error('Failed to update patient consultation status', e);
		}
	}
	
	scrollToBottom(500);
	textInput.value = '';
}

function requestFileBrowser() {
	browser.value.click();
}

import { PostExamination } from 'src/adaptor/PostExamination';

async function uploadExamination() {
	const list = browser.value.files as FileList;

	if (list.length === 0) {
		return;
	}

	await PostExamination(session, list[0]);
}

import { GenerateReport } from 'src/adaptor/GenerateReport';

async function generateReport() {
	await GenerateReport(session);
}

defineOptions({ name: 'Page.InteractionPanel' });
</script>

<style lang="scss">
#page-interaction {
	.text-h6 {
		font-size: 16px;
	}

	background-color: #f4f5fa;

	.q-header {
		background-color: #f4f5fa;
	}

	.q-footer {
		background-color: #ffffff;
	}

	.q-btn.gradient {
		background-image: linear-gradient(to right, #fff, #eee, #fff);
	}

	$bubble-blank: 48px;

	.q-message-sent {
		padding-left: $bubble-blank;

		.q-message-text {
			background-color: #cae2eb;
		}
	}

	.q-message-name {
		color: #bbb;
	}

	.q-message-received {
		padding-right: $bubble-blank;
	}

	.q-message-text {
		min-height: 0;

		padding: 1em;

		&::before {
			content: none;
		}

		&.q-message-text--received {
			border-top-left-radius: 0;
			border-bottom-left-radius: $generic-border-radius;
		}

		&.q-message-text--sent {
			border-top-right-radius: 0;
			border-bottom-right-radius: $generic-border-radius;
		}
	}
}
</style>
