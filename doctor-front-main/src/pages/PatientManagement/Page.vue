<template>
	<q-layout view="lHh Lpr lFf">
		<!-- 密码验证弹窗 -->
		<q-dialog v-model="passwordDialog" persistent>
			<q-card style="min-width: 350px">
				<q-card-section class="row items-center bg-primary text-white">
					<q-avatar icon="lock" text-color="white" />
					<span class="q-ml-sm text-subtitle1 text-weight-bold">访问验证</span>
				</q-card-section>
				
				<q-card-section class="q-pt-lg">
					<p>请输入密码以访问就诊人管理系统：</p>
					<q-input 
						v-model="password" 
						filled 
						:type="showPassword ? 'text' : 'password'"
						label="访问密码" 
						ref="passwordInput"
						:error="passwordError"
						:error-message="passwordErrorMsg"
						@keyup.enter="verifyPassword"
					>
						<template v-slot:append>
							<q-icon
								:name="showPassword ? 'visibility_off' : 'visibility'"
								class="cursor-pointer"
								@click="showPassword = !showPassword"
							/>
						</template>
					</q-input>
				</q-card-section>
				
				<q-card-actions align="right">
					<q-btn unelevated label="验证" color="primary" @click="verifyPassword" />
				</q-card-actions>
			</q-card>
		</q-dialog>

		<q-header elevated class="bg-primary text-white" v-if="isAuthenticated">
			<q-toolbar>
				<q-btn
					flat
					dense
					round
					icon="arrow_back"
					aria-label="返回首页"
					:to="{ name: 'app.index' }"
				/>

				<q-toolbar-title>
					<span class="text-weight-bold">就诊人管理系统</span>
					<q-badge color="secondary" class="q-ml-sm">共{{ patients.length }}人</q-badge>
				</q-toolbar-title>
				
				<q-space />
				
				<q-btn flat round dense icon="help_outline">
					<q-tooltip>帮助信息</q-tooltip>
				</q-btn>
			</q-toolbar>
			
			<!-- 搜索栏 -->
			<q-toolbar class="bg-primary-dark">
				<q-input
					v-model="searchText"
					filled
					dense
					dark
					placeholder="搜索就诊人姓名或病历号..."
					class="full-width q-mx-md"
					@keyup.enter="searchPatients"
				>
					<template v-slot:prepend>
						<q-icon name="search" />
					</template>
					<template v-slot:append>
						<q-icon name="clear" class="cursor-pointer" v-if="searchText" @click="searchText = ''" />
					</template>
				</q-input>
			</q-toolbar>
		</q-header>

		<q-page-container v-if="isAuthenticated">
			<q-page padding>
				<div class="row justify-between items-center q-mb-md">
					<div class="text-h5 text-primary text-weight-medium">就诊人列表</div>
					<div>
						<q-btn
							color="secondary"
							icon="refresh"
							label="刷新会话状态"
							:flat="!isRefreshing"
							:outline="isRefreshing"
							class="q-mr-md"
							:loading="isRefreshing"
							@click="refreshPatientConsultationData"
						>
							<q-tooltip>
								从服务器获取最新问诊数据。如果问诊次数不正确，请点击此按钮刷新数据。
							</q-tooltip>
						</q-btn>
						<q-btn
							color="primary"
							icon="add"
							label="添加就诊人"
							unelevated
							@click="openAddDialog"
						/>
					</div>
				</div>
				
				<!-- 信息卡片 -->
				<q-card flat bordered class="q-mb-md bg-blue-1">
					<q-card-section class="row items-center">
						<q-icon name="info" color="info" size="sm" class="q-mr-sm" />
						<div class="text-body2">该系统用于管理所有就诊人信息，包括姓名、病历号、链接和问诊状态，您可以添加、编辑或删除就诊人信息。</div>
					</q-card-section>
				</q-card>

				<!-- 患者列表表格 -->
				<q-card flat bordered>
					<q-table
						:rows="filteredPatients"
						:columns="columns"
						row-key="uid"
						no-data-label="没有找到就诊人记录"
						v-model:pagination="pagination"
						flat
						:loading="false"
						class="full-width"
					>
						<template v-slot:header="props">
							<q-tr :props="props">
								<q-th v-for="col in props.cols" :key="col.name" :props="props" class="bg-grey-2">
									{{ col.label }}
								</q-th>
							</q-tr>
						</template>
						
						<template v-slot:body="props">
							<q-tr :props="props" :class="{'bg-blue-1': props.rowIndex % 2 === 0}">
								<q-td key="name" :props="props">
									<div class="text-weight-medium">{{ props.row.name }}</div>
								</q-td>
								<q-td key="gender" :props="props">
									{{ props.row.gender }}
								</q-td>
								<q-td key="age" :props="props">
									{{ props.row.age }}
								</q-td>
								<q-td key="medical_record_number" :props="props">
									<q-chip v-if="props.row.medical_record_number" dense outline color="primary" text-color="primary" size="sm">
										{{ props.row.medical_record_number }}
									</q-chip>
									<span v-else class="text-grey-6">暂无</span>
								</q-td>
								<q-td key="notes" :props="props">
									{{ props.row.notes }}
								</q-td>
								<q-td key="link" :props="props">
									<div class="row justify-center no-wrap">
										<q-btn flat round size="sm" color="primary" icon="visibility" @click="openInteractionPage(props.row)">
											<q-tooltip>查阅</q-tooltip>
										</q-btn>
										<q-btn flat round size="sm" color="secondary" icon="content_copy" @click="copyPatientInfo(props.row)">
											<q-tooltip>复制信息</q-tooltip>
										</q-btn>
									</div>
								</q-td>
								<q-td key="casebookLink" :props="props">
									<div class="row justify-center">
										<q-btn flat round size="sm" color="primary" icon="menu_book" @click="openCasebookPage(props.row)">
											<q-tooltip>查看病历</q-tooltip>
										</q-btn>
									</div>
								</q-td>
								<q-td key="consultationCount" :props="props" class="text-center">
									<div class="row justify-center items-center">
										<q-chip outline color="accent" text-color="accent" size="sm" class="q-mr-xs">
											{{ props.row.consultationCount }}
										</q-chip>
										<q-btn flat dense round size="xs" color="grey" icon="refresh" @click="refreshSinglePatient(props.row)">
											<q-tooltip>更新问诊次数</q-tooltip>
										</q-btn>
									</div>
								</q-td>
								<q-td key="consulted" :props="props" class="text-center">
									<q-badge :color="props.row.consulted ? 'positive' : 'grey'" :label="props.row.consulted ? '已问诊' : '未问诊'" />
								</q-td>
								<q-td key="createdAt" :props="props" class="text-center">
									{{ new Date(props.row.createdAt).toLocaleString() }}
								</q-td>
								<q-td key="actions" :props="props" class="text-center">
									<div class="row justify-center no-wrap">
										<q-btn flat round size="sm" color="primary" icon="edit" @click="editPatient(props.row)">
											<q-tooltip>编辑</q-tooltip>
										</q-btn>
										<q-btn flat round size="sm" color="negative" icon="delete" @click="deletePatient(props.row)">
											<q-tooltip>删除</q-tooltip>
										</q-btn>
										<q-btn flat round size="sm" color="secondary" icon="launch" @click="openInteractionPage(props.row)">
											<q-tooltip>打开问诊页面</q-tooltip>
										</q-btn>
									</div>
								</q-td>
							</q-tr>
						</template>
						
						<template v-slot:bottom="scope">
							<div class="row items-center justify-between full-width q-px-sm">
								<div class="text-body2 text-grey">
									显示 {{ filteredPatients.length > 0 ? scope.pagination.rowsPerPage * (scope.pagination.page - 1) + 1 : 0 }}-{{ Math.min(scope.pagination.rowsPerPage * scope.pagination.page, filteredPatients.length) }} 条，共 {{ filteredPatients.length }} 条
								</div>
								<q-pagination
									v-model="pagination.page"
									:max="Math.ceil(filteredPatients.length / pagination.rowsPerPage)"
									:boundary-links="true"
									:direction-links="true"
									:input="true"
									input-class="q-ml-md"
									size="sm"
								/>
							</div>
						</template>

						<template v-slot:no-data>
							<div class="full-width row flex-center q-py-lg">
								<q-icon name="sentiment_dissatisfied" size="2rem" color="grey-6" class="q-mb-sm" />
								<div class="text-grey-6">暂无就诊人记录，请添加新就诊人</div>
							</div>
						</template>
					</q-table>
				</q-card>
			</q-page>
		</q-page-container>
		
		<q-footer bordered class="bg-white text-grey-8" v-if="isAuthenticated">
			<q-toolbar>
				<q-toolbar-title class="text-caption">
					DoctorX 医疗系统 © 2025 版权所有
				</q-toolbar-title>
			</q-toolbar>
		</q-footer>

		<!-- 添加/编辑就诊人对话框 -->
		<q-dialog v-model="addDialog" persistent>
			<q-card style="min-width: 450px; max-width: 80vw;">
				<q-bar class="bg-primary text-white">
					<div class="text-weight-bold">{{ isEditing ? '编辑就诊人' : '添加就诊人' }}</div>
					<q-space />
					<q-btn dense flat icon="close" v-close-popup>
						<q-tooltip>关闭</q-tooltip>
					</q-btn>
				</q-bar>
				
				<q-card-section class="q-pt-lg">
					<q-form @submit="isEditing ? updatePatient() : addPatient()">
						<q-input
							v-model="newPatient.name"
							label="就诊人姓名 *"
							outlined
							stack-label
							:rules="[(val: string) => !!val || '请输入姓名']"
							:disable="isEditing && editingOriginalUid !== ''"
							class="q-mb-md"
							clearable
						>
							<template v-slot:prepend>
								<q-icon name="person" color="primary" />
							</template>
							<template v-slot:hint>请输入就诊人的真实姓名</template>
						</q-input>
						
						<div class="row q-col-gutter-md q-mb-md">
							<div class="col-6">
								<q-select
									v-model="newPatient.gender"
									:options="['男', '女']"
									label="性别 *"
									outlined
									stack-label
									:rules="[(val: string) => !!val || '请选择性别']"
									map-options
									emit-value
								>
									<template v-slot:prepend>
										<q-icon name="wc" color="primary" />
									</template>
								</q-select>
							</div>
							<div class="col-6">
								<q-input
									v-model.number="newPatient.age"
									type="number"
									label="年龄 *"
									outlined
									stack-label
									:rules="[
										(val: number) => val !== null && val !== undefined || '请输入年龄',
										(val: number) => val >= 0 && val <= 120 || '年龄必须在0-120之间',
									]"
								>
									<template v-slot:prepend>
										<q-icon name="cake" color="primary" />
									</template>
								</q-input>
							</div>
						</div>
						
						<q-input
							v-model="newPatient.medical_record_number"
							label="病历号"
							outlined
							stack-label
							hint="可选，请输入患者的病历号（必须唯一）"
							clearable
							class="q-mb-md"
							:rules="[
								(val: string) => !val || !isMedicalRecordNumberExists(val, isEditing ? editingOriginalUid.value : undefined) || '此病历号已被使用，请输入其他病历号'
							]"
							lazy-rules
							@update:model-value="validateMedicalRecordNumber"
						>
							<template v-slot:prepend>
								<q-icon name="assignment" color="primary" />
							</template>
						</q-input>
						
						<q-input
							v-model="newPatient.notes"
							label="备注"
							outlined
							stack-label
							type="textarea"
							autogrow
							hint="可选填写备注信息"
							class="q-mb-md"
						>
							<template v-slot:prepend>
								<q-icon name="note" color="primary" />
							</template>
						</q-input>
					</q-form>
				</q-card-section>
				
				<q-separator />
				
				<q-card-actions align="right">
					<q-btn flat label="取消" color="grey" v-close-popup />
					<q-btn 
						:label="isEditing ? '保存' : '添加'" 
						color="primary" 
						unelevated
						@click="isEditing ? updatePatient() : addPatient()" 
						:disable="!isFormValid"
					/>
				</q-card-actions>
			</q-card>
		</q-dialog>
		
		<!-- 删除确认对话框 -->
		<q-dialog v-model="deleteDialog" persistent>
			<q-card style="min-width: 350px">
				<q-card-section class="row items-center bg-negative text-white">
					<q-avatar icon="warning" text-color="white" />
					<span class="q-ml-sm text-subtitle1 text-weight-bold">确认删除</span>
				</q-card-section>
				
				<q-card-section class="q-pt-lg">
					<p>您确定要删除就诊人 <strong>{{ patientToDelete?.name }}</strong> 吗？</p>
					<p class="text-caption text-negative">此操作不可恢复，删除后相关问诊记录将无法访问。</p>
				</q-card-section>
				
				<q-card-actions align="right">
					<q-btn flat label="取消" color="primary" v-close-popup />
					<q-btn unelevated label="确认删除" color="negative" @click="confirmDelete" v-close-popup />
				</q-card-actions>
			</q-card>
		</q-dialog>
	</q-layout>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { Notify } from 'quasar';

interface Patient {
	name: string;
	uid: string;
	medical_record_number: string;
	link: string;
	consultationCount: number;
	consulted: boolean;
	gender: string;
	age: number;
	notes: string;
	createdAt: string;
	casebookLink: string;
}

// 定义API基础URL - 使用完整的URL，不要使用相对路径
import { API_BASE_URL } from 'src/adaptor/Api';
// 打印API基础URL用于调试
console.log('API基础URL:', API_BASE_URL);

export default defineComponent({
	name: 'PatientManagementPage',
	setup() {
		const searchText = ref('');
		const addDialog = ref(false);
		const deleteDialog = ref(false);
		const patients = ref<Patient[]>([]);
		const newPatient = ref({
			name: '',
			gender: '',
			age: 0,
			notes: '',
			medical_record_number: '',
		});
		const isEditing = ref(false);
		const editingOriginalUid = ref('');
		const patientToDelete = ref<Patient | null>(null);
		const isRefreshing = ref(false);
		// 密码保护相关
		const passwordDialog = ref(true);
		const password = ref('');
		const showPassword = ref(false);
		const isAuthenticated = ref(false);
		const passwordError = ref(false);
		const passwordErrorMsg = ref('');
		const passwordInput = ref(null);
		// 自动刷新计时器
		let autoRefreshTimer: number | null = null;

		const pagination = ref({
			sortBy: 'name',
			descending: false,
			page: 1,
			rowsPerPage: 10,
			rowsNumber: 0,
		});

		const columns = [
			{ name: 'name', required: true, label: '就诊人姓名', align: 'left' as const, field: 'name', sortable: true },
			{ name: 'gender', required: true, label: '性别', align: 'center' as const, field: 'gender', sortable: true },
			{ name: 'age', required: true, label: '年龄', align: 'center' as const, field: 'age', sortable: true },
			{ name: 'medical_record_number', required: false, label: '病历号', align: 'left' as const, field: 'medical_record_number', sortable: true },
			{ name: 'notes', align: 'left' as const, label: '备注', field: 'notes' },
			{ name: 'link', align: 'center' as const, label: '问诊链接', field: 'link' },
			{ name: 'casebookLink', align: 'center' as const, label: '病历链接', field: 'casebookLink' },
			{ name: 'consultationCount', align: 'center' as const, label: '问诊次数', field: 'consultationCount', sortable: true },
			{ name: 'consulted', align: 'center' as const, label: '问诊状态', field: 'consulted', sortable: true },
			{ name: 'createdAt', align: 'center' as const, label: '创建时间', field: 'createdAt', sortable: true },
			{ name: 'actions', align: 'center' as const, label: '操作', field: 'actions' },
		];

		const filteredPatients = computed(() => {
			if (!searchText.value) return patients.value;
			const query = searchText.value.toLowerCase();
			return patients.value.filter(
				patient => patient.name.toLowerCase().includes(query) || 
					(patient.medical_record_number && patient.medical_record_number.toLowerCase().includes(query)),
			);
		});

		const isFormValid = computed(() => {
			const basicFieldsValid = newPatient.value.name && 
				newPatient.value.gender && 
				newPatient.value.age !== null && 
				newPatient.value.age >= 0 && 
				newPatient.value.age <= 120;
				
			// 检查病历号唯一性
			const medicalRecordNumberValid = !newPatient.value.medical_record_number || 
				!isMedicalRecordNumberExists(newPatient.value.medical_record_number, isEditing.value ? editingOriginalUid.value : undefined);
			
			return basicFieldsValid && medicalRecordNumberValid;
		});

		// 检查病历号是否已存在
		function isMedicalRecordNumberExists(medicalRecordNumber: string, excludeUid?: string): boolean {
			// 如果病历号为空，则返回false（允许空病历号）
			if (!medicalRecordNumber) return false;
			
			// 检查是否有其他患者使用了相同的病历号
			return patients.value.some(patient => 
				patient.medical_record_number === medicalRecordNumber && 
				(!excludeUid || patient.uid !== excludeUid),
			);
		}

		function openAddDialog() {
			isEditing.value = false;
			editingOriginalUid.value = '';
			newPatient.value = { name: '', gender: '', age: 0, notes: '', medical_record_number: '' };
			addDialog.value = true;
		}

		function openEditDialog(patient: Patient) {
			isEditing.value = true;
			editingOriginalUid.value = patient.uid;
			newPatient.value = { 
				name: patient.name, 
				gender: patient.gender, 
				age: patient.age, 
				notes: patient.notes,
				medical_record_number: patient.medical_record_number || '',
			};
			addDialog.value = true;
		}

		function isUidExists(uid: string) {
			return patients.value.some(p => p.uid === uid);
		}

		// 获取单个患者的会话轮数 - 标记为未使用，但保留以备将来使用
		// eslint-disable-next-line @typescript-eslint/no-unused-vars
		async function fetchPatientConsultationRounds(uid: string): Promise<{rounds: number, hasConsulted: boolean}> {
			try {
				const response = await fetch(`${API_BASE_URL}/get_conversation_rounds?uid=${encodeURIComponent(uid)}`, {
					method: 'GET',
					headers: {
						'Content-Type': 'application/json',
					},
				});
				
				if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
				}
				
				const data = await response.json();
				return {
					rounds: data.rounds,
					hasConsulted: data.hasConsulted,
				};
			} catch (error) {
				console.error(`获取患者 ${uid} 的会话轮数失败:`, error);
				return { rounds: 0, hasConsulted: false };
			}
		}

		// 批量获取多个患者的会话轮数
		async function fetchMultiplePatientConsultationRounds(uids: string[]): Promise<{uid: string, rounds: number, hasConsulted: boolean}[]> {
			if (uids.length === 0) return [];
			
			try {
				const response = await fetch(`${API_BASE_URL}/get_multiple_conversation_rounds`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({ uids }),
				});
				
				if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
				}
				
				const data = await response.json();
				return data.results;
			} catch (error) {
				console.error('批量获取患者会话轮数失败:', error);
				return uids.map(uid => ({ uid, rounds: 0, hasConsulted: false }));
			}
		}

		// 刷新所有患者的会话数据
		async function refreshPatientConsultationData() {
			if (patients.value.length === 0) return;
			
			isRefreshing.value = true;
			
			try {
				// 获取所有患者的UID
				const uids = patients.value.map(patient => patient.uid);
				
				// 批量获取会话轮数
				const results = await fetchMultiplePatientConsultationRounds(uids);
				
				// 更新患者数据
				for (const result of results) {
					const patientIndex = patients.value.findIndex(p => p.uid === result.uid);
					if (patientIndex !== -1) {
						patients.value[patientIndex].consultationCount = result.rounds;
						patients.value[patientIndex].consulted = result.hasConsulted;
					}
				}
				
				// 从服务器重新获取完整的患者数据，以确保同步
				const response = await fetch(`${API_BASE_URL}/patients`, {
					method: 'GET',
					headers: {
						'Content-Type': 'application/json',
					},
				});
				
				if (response.ok) {
					const data = await response.json();
					if (data.status === 'success') {
						// 使用服务器上的最新数据
						patients.value = data.patients;
					}
				}
				
				// 更新本地存储以保持同步
				localStorage.setItem('patientData', JSON.stringify(patients.value));
				
				// 使用Notify而不是$q.notify
				Notify.create({
					color: 'positive',
					message: '问诊数据已更新',
					icon: 'update',
					position: 'top',
					timeout: 2000,
				});
			} catch (error) {
				console.error('刷新患者会话数据失败:', error);
				// 使用Notify而不是$q.notify
				Notify.create({
					color: 'negative',
					message: '更新问诊数据失败，请稍后重试',
					icon: 'error',
					position: 'top',
					timeout: 2000,
				});
			} finally {
				isRefreshing.value = false;
			}
		}

		// 加载患者数据（只在验证通过后调用）
		async function loadPatientData() {
			try {
				// 从服务器加载患者数据
				const response = await fetch(`${API_BASE_URL}/patients`, {
					method: 'GET',
					headers: {
						'Content-Type': 'application/json',
					},
				});
				
				if (response.ok) {
					const data = await response.json();
					if (data.status === 'success') {
						patients.value = data.patients;
					} else {
						console.error('加载患者数据失败:', data.message);
						Notify.create({
							color: 'negative',
							message: '无法加载患者数据，请稍后重试',
							icon: 'error',
							position: 'top',
							timeout: 2000,
						});
					}
				} else {
					console.error('加载患者数据失败:', response.statusText);
					
					// 如果服务器加载失败，尝试从本地存储加载数据并导入到服务器
					const savedPatients = localStorage.getItem('patientData');
					if (savedPatients) {
						const parsedPatients = JSON.parse(savedPatients);
						patients.value = parsedPatients;
						
						// 将本地存储的数据导入到服务器
						await importLocalPatients(parsedPatients);
					}
				}
				
				// 加载完数据后立即从服务器获取最新状态
				refreshPatientConsultationData();
				
				// 设置自动刷新
				setupAutoRefresh();
			} catch (e) {
				console.error('加载患者数据失败:', e);
				
				// 如果服务器加载失败，尝试从本地存储加载数据
				const savedPatients = localStorage.getItem('patientData');
				if (savedPatients) {
					patients.value = JSON.parse(savedPatients);
					
					// 将本地存储的数据导入到服务器
					await importLocalPatients(patients.value);
				}
			}
		}

		// 将本地存储的患者数据导入到服务器
		async function importLocalPatients(patientsData: Patient[]) {
			try {
				const response = await fetch(`${API_BASE_URL}/import_local_patients`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						patients: patientsData,
					}),
				});
				
				if (response.ok) {
					const data = await response.json();
					console.log('本地患者数据导入结果:', data.message);
				} else {
					console.error('导入本地患者数据失败:', response.statusText);
				}
			} catch (e) {
				console.error('导入本地患者数据出错:', e);
			}
		}

		function addPatient() {
			if (!isFormValid.value) return;
			
			// 检查病历号是否已存在
			if (newPatient.value.medical_record_number && isMedicalRecordNumberExists(newPatient.value.medical_record_number)) {
				Notify.create({
					color: 'negative',
					message: `添加失败: 病历号 ${newPatient.value.medical_record_number} 已存在`,
					icon: 'error',
					position: 'top',
					timeout: 3000,
				});
				return;
			}
			
			const patient = {
				name: newPatient.value.name,
				gender: newPatient.value.gender,
				age: newPatient.value.age,
				notes: newPatient.value.notes,
				medical_record_number: newPatient.value.medical_record_number,
				// UID will be auto-generated by the server
				consultationCount: 0,
				consulted: false,
				createdAt: new Date().toISOString(),
			};
			
			// 将患者信息发送到服务器
			fetch(`${API_BASE_URL}/patients`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(patient),
			})
				.then(response => response.json())
				.then(data => {
					if (data.status === 'success') {
						// 如果服务器返回了完整的患者信息（包括自动生成的UID和链接）
						if (data.patient) {
							// 添加到本地数组
							patients.value.push(data.patient);
						} else {
							// 如果服务器没有返回完整信息，则刷新患者列表
							refreshPatientConsultationData();
						}
						
						// 更新本地存储以保持同步
						localStorage.setItem('patientData', JSON.stringify(patients.value));
						
						addDialog.value = false;
						
						Notify.create({
							color: 'positive',
							message: `就诊人 ${patient.name} 添加成功`,
							icon: 'check_circle',
							position: 'top',
							timeout: 2000,
						});
					} else {
						Notify.create({
							color: 'negative',
							message: `添加失败: ${data.message}`,
							icon: 'error',
							position: 'top',
							timeout: 2000,
						});
					}
				})
				.catch(error => {
					console.error('添加患者失败:', error);
					Notify.create({
						color: 'negative',
						message: '添加失败，请稍后重试',
						icon: 'error',
						position: 'top',
						timeout: 2000,
					});
				});
		}

		function updatePatient() {
			if (!isFormValid.value) return;
			
			// 检查病历号是否已存在（排除当前编辑的患者）
			if (newPatient.value.medical_record_number && 
				isMedicalRecordNumberExists(newPatient.value.medical_record_number, editingOriginalUid.value)) {
				Notify.create({
					color: 'negative',
					message: `更新失败: 病历号 ${newPatient.value.medical_record_number} 已被其他就诊人使用`,
					icon: 'error',
					position: 'top',
					timeout: 3000,
				});
				return;
			}
			
			// 找到要编辑的患者
			const index = patients.value.findIndex(p => p.uid === editingOriginalUid.value);
			if (index !== -1) {
				// 使用正确的URL格式：localhost:8504/?uid=${uid}#/interaction
				const origin = window.location.origin;
				const link = `${origin}/?uid=${editingOriginalUid.value}#/interaction`;
				const casebookLink = `${origin}/?uid=${editingOriginalUid.value}#/casebook/small`;
				
				// 更新患者信息对象 - 包含所有必要字段
				const updatedPatient = {
					name: newPatient.value.name,
					gender: newPatient.value.gender,
					age: newPatient.value.age,
					notes: newPatient.value.notes || '',
					medical_record_number: newPatient.value.medical_record_number || '',
					link,
					casebookLink,
					uid: editingOriginalUid.value,  // 确保包含UID
					consultationCount: patients.value[index].consultationCount || 0,
					consulted: patients.value[index].consulted || false,
					createdAt: patients.value[index].createdAt || new Date().toISOString(),
				};
				
				// 构建API URL
				const apiUrl = `${API_BASE_URL}/patients/${editingOriginalUid.value}`;
				console.log('更新患者API URL:', apiUrl);
				console.log('正在更新患者数据:', updatedPatient);
				
				// 将更新发送到服务器 - 使用XMLHttpRequest以获取更详细的错误信息
				const xhr = new XMLHttpRequest();
				xhr.open('PUT', apiUrl, true);
				xhr.setRequestHeader('Content-Type', 'application/json');
				xhr.setRequestHeader('Accept', 'application/json');
				
				xhr.onload = function () {
					console.log('更新患者响应状态:', xhr.status);
					console.log('更新患者响应全文:', xhr.responseText);
					
					let data;
					try {
						data = JSON.parse(xhr.responseText);
					} catch (e) {
						console.error('解析JSON响应失败:', e);
						data = { status: 'error', message: xhr.responseText || '未知错误' };
					}
					
					console.log('更新患者响应数据:', data);
					
					if (xhr.status >= 200 && xhr.status < 300 && data.status === 'success') {
						// 更新本地数组中的患者信息
						patients.value[index].name = newPatient.value.name;
						patients.value[index].gender = newPatient.value.gender;
						patients.value[index].age = newPatient.value.age;
						patients.value[index].notes = newPatient.value.notes;
						patients.value[index].medical_record_number = newPatient.value.medical_record_number;
						patients.value[index].link = link;
						patients.value[index].casebookLink = casebookLink;
						
						// 更新本地存储以保持同步
						localStorage.setItem('patientData', JSON.stringify(patients.value));
						
						addDialog.value = false;
						
						Notify.create({
							color: 'positive',
							message: `就诊人 ${newPatient.value.name} 信息已更新`,
							icon: 'check_circle',
							position: 'top',
							timeout: 2000,
						});
						
						// 编辑后刷新数据
						refreshPatientConsultationData();
					} else {
						Notify.create({
							color: 'negative',
							message: `更新失败: ${data.message || '未知错误'} (状态码: ${xhr.status})`,
							icon: 'error',
							position: 'top',
							timeout: 3000,
						});
					}
				};
				
				xhr.onerror = function () {
					console.error('更新患者请求失败:', xhr.statusText);
					Notify.create({
						color: 'negative',
						message: '网络错误，无法连接到服务器',
						icon: 'error',
						position: 'top',
						timeout: 3000,
					});
				};
				
				xhr.send(JSON.stringify(updatedPatient));
			}
		}

		function editPatient(patientToEdit: Patient) {
			openEditDialog(patientToEdit);
		}

		function deletePatient(patientInput: Patient) {
			patientToDelete.value = patientInput;
			deleteDialog.value = true;
		}

		function confirmDelete() {
			if (!patientToDelete.value) return;
			
			const uid = patientToDelete.value.uid;
			const index = patients.value.findIndex(p => p.uid === uid);
			
			if (index !== -1) {
				const deletedName = patientToDelete.value.name;
				
				// 构建API URL
				const apiUrl = `${API_BASE_URL}/patients/${uid}`;
				console.log('删除患者API URL:', apiUrl);
				
				// 从服务器删除患者 - 使用XMLHttpRequest以获取更详细的错误信息
				const xhr = new XMLHttpRequest();
				xhr.open('DELETE', apiUrl, true);
				xhr.setRequestHeader('Content-Type', 'application/json');
				xhr.setRequestHeader('Accept', 'application/json');
				
				xhr.onload = function () {
					console.log('删除患者响应状态:', xhr.status);
					console.log('删除患者响应全文:', xhr.responseText);
					
					let data;
					try {
						data = JSON.parse(xhr.responseText);
					} catch (e) {
						console.error('解析JSON响应失败:', e);
						data = { status: 'error', message: xhr.responseText || '未知错误' };
					}
					
					console.log('删除患者响应数据:', data);
					
					if (xhr.status >= 200 && xhr.status < 300 && data.status === 'success') {
						// 从本地数组中删除患者
						patients.value.splice(index, 1);
						
						// 更新本地存储以保持同步
						localStorage.setItem('patientData', JSON.stringify(patients.value));
						
						Notify.create({
							color: 'positive',
							message: `就诊人 ${deletedName} 已删除`,
							icon: 'check_circle',
							position: 'top',
							timeout: 2000,
						});
					} else {
						Notify.create({
							color: 'negative',
							message: `删除失败: ${data.message || '未知错误'} (状态码: ${xhr.status})`,
							icon: 'error',
							position: 'top',
							timeout: 3000,
						});
					}
					
					patientToDelete.value = null;
				};
				
				xhr.onerror = function () {
					console.error('删除患者请求失败:', xhr.statusText);
					Notify.create({
						color: 'negative',
						message: '网络错误，无法连接到服务器',
						icon: 'error',
						position: 'top',
						timeout: 3000,
					});
					patientToDelete.value = null;
				};
				
				xhr.send();
			}
		}

		function searchPatients() {
			// 触发搜索，实际上搜索是实时的通过计算属性实现的
			pagination.value.page = 1; // 重置到第一页
		}

		function openInteractionPage(patient: Patient) {
			// 使用正确的URL格式：localhost:8504/?uid=${uid}#/interaction
			const origin = window.location.origin;
			const url = `${origin}/?uid=${encodeURIComponent(patient.uid)}#/interaction`;
			window.open(url, '_blank');
		}

		function openCasebookPage(patient: Patient) {
			// 打开病历页面
			const origin = window.location.origin;
			const url = `${origin}/?uid=${encodeURIComponent(patient.uid)}#/casebook/small`;
			window.open(url, '_blank');
		}

		function copyPatientInfo(patient: Patient) {
			// 复制患者基本信息到剪贴板
			const info = `姓名：${patient.name}\n性别：${patient.gender}\n年龄：${patient.age}\n病历号：${patient.medical_record_number || '无'}\n备注：${patient.notes || '无'}`;
			
			navigator.clipboard.writeText(info).then(() => {
				Notify.create({
					color: 'positive',
					message: '患者信息已复制到剪贴板',
					icon: 'content_copy',
					position: 'top',
					timeout: 2000,
				});
			}).catch(err => {
				console.error('复制失败:', err);
				Notify.create({
					color: 'negative',
					message: '复制失败，请手动复制',
					icon: 'error',
					position: 'top',
					timeout: 2000,
				});
			});
		}

		// 设置自动刷新计时器（每60秒更新一次）
		function setupAutoRefresh() {
			autoRefreshTimer = window.setInterval(() => {
				refreshPatientConsultationData();
			}, 60000); // 60秒自动刷新
		}

		// 清除自动刷新计时器
		function clearAutoRefresh() {
			if (autoRefreshTimer !== null) {
				clearInterval(autoRefreshTimer);
				autoRefreshTimer = null;
			}
		}

		// 密码验证函数
		function verifyPassword() {
			if (process.env.PATIENT_MANAGEMENT_PASSWORD && password.value === process.env.PATIENT_MANAGEMENT_PASSWORD) {
				passwordDialog.value = false;
				isAuthenticated.value = true;
				
				// 身份验证通过后加载数据
				loadPatientData();
				
				// 使用Notify而不是$q.notify
				Notify.create({
					color: 'positive',
					message: '验证成功，欢迎使用就诊人管理系统',
					icon: 'check_circle',
					position: 'top',
					timeout: 2000,
				});
			} else {
				passwordError.value = true;
				passwordErrorMsg.value = '密码错误，请重试';
				password.value = '';
				
				// 震动效果
				// 使用Notify而不是$q.notify
				Notify.create({
					color: 'negative',
					message: '密码错误',
					icon: 'error',
					position: 'top',
					timeout: 1500,
				});
			}
		}

		// 在组件挂载时处理
		onMounted(async () => {
			// 聚焦到密码输入框
			setTimeout(() => {
				// @ts-expect-error - passwordInput.value might be null but we still want to try focusing
				passwordInput.value?.focus();
			}, 300);
		});

		// 组件卸载前清除计时器
		onBeforeUnmount(() => {
			clearAutoRefresh();
		});

		// 在适当位置添加validateMedicalRecordNumber函数
		function validateMedicalRecordNumber(value: string) {
			// 如果病历号为空，不进行验证
			if (!value) return;
			
			// 检查病历号是否已存在
			if (isMedicalRecordNumberExists(value, isEditing.value ? editingOriginalUid.value : undefined)) {
				// 使用Notify提示用户
				Notify.create({
					color: 'warning',
					message: '此病历号已被其他就诊人使用，请输入其他病历号',
					icon: 'warning',
					position: 'top',
					timeout: 3000,
				});
			}
		}

		// 刷新单个患者的问诊数据
		async function refreshSinglePatient(patient: Patient) {
			try {
				// 从服务器获取最新的问诊轮数
				const response = await fetch(`${API_BASE_URL}/get_conversation_rounds?uid=${encodeURIComponent(patient.uid)}`, {
					method: 'GET',
					headers: {
						'Content-Type': 'application/json',
					},
				});
				
				if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
				}
				
				const data = await response.json();
				
				// 更新本地患者数据
				const index = patients.value.findIndex(p => p.uid === patient.uid);
				if (index !== -1) {
					patients.value[index].consultationCount = data.rounds;
					patients.value[index].consulted = data.hasConsulted;
					
					// 更新本地存储
					localStorage.setItem('patientData', JSON.stringify(patients.value));
					
					Notify.create({
						color: 'positive',
						message: `已更新 ${patient.name} 的问诊数据`,
						icon: 'update',
						position: 'top',
						timeout: 2000,
					});
				}
			} catch (error) {
				console.error(`刷新患者 ${patient.uid} 的问诊数据失败:`, error);
				Notify.create({
					color: 'negative',
					message: '更新问诊数据失败，请稍后重试',
					icon: 'error',
					position: 'top',
					timeout: 2000,
				});
			}
		}

		return {
			searchText,
			patients,
			filteredPatients,
			columns,
			addDialog,
			deleteDialog,
			newPatient,
			pagination,
			isFormValid,
			isEditing,
			editingOriginalUid,
			patientToDelete,
			isRefreshing,
			openAddDialog,
			openEditDialog,
			addPatient,
			updatePatient,
			editPatient,
			deletePatient,
			confirmDelete,
			searchPatients,
			isUidExists,
			openInteractionPage,
			openCasebookPage,
			copyPatientInfo,
			refreshPatientConsultationData,
			// 密码保护相关
			passwordDialog,
			password,
			showPassword,
			isAuthenticated,
			passwordError,
			passwordErrorMsg,
			passwordInput,
			verifyPassword,
			validateMedicalRecordNumber,
			isMedicalRecordNumberExists,
			refreshSinglePatient,
		};
	},
});
</script>

<style scoped>
.q-table tbody td {
	white-space: normal;
}

.bg-primary-dark {
	background-color: rgba(0, 0, 0, 0.1);
}

/* 表格样式 */
.q-table th {
	font-weight: 500;
}

.q-table tr:hover {
	background-color: #f0f8ff !important;
}

/* 超链接样式 */
a {
	text-decoration: none;
	transition: color 0.3s;
}

a:hover {
	text-decoration: underline;
	color: #1976d2;
}

/* 添加卡片悬浮效果 */
.q-card {
	transition: box-shadow 0.3s, transform 0.3s;
}

.q-card:hover {
	box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.ellipsis {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}
</style> 