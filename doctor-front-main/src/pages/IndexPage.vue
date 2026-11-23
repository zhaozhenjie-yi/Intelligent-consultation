<template>
	<q-page class="row items-center justify-evenly" padding>
		<div class="text-center">
			<div class="text-h3 q-mb-xl">DoctorX 医疗系统</div>
			
			<div class="row q-col-gutter-md justify-center">
				<div class="col-12 col-sm-6 col-md-3">
					<q-card class="text-center q-pa-md" clickable @click="$router.push({ name: 'app.patient.management' })">
						<q-card-section>
							<q-icon name="people" size="4rem" color="primary" />
						</q-card-section>
						<q-card-section>
							<div class="text-h6">就诊人管理</div>
							<div class="text-caption">添加和管理就诊人信息</div>
						</q-card-section>
					</q-card>
				</div>
				
				<div class="col-12 col-sm-6 col-md-3">
					<q-card class="text-center q-pa-md" clickable @click="$router.push({ name: 'app.interaction' })">
						<q-card-section>
							<q-icon name="chat" size="4rem" color="secondary" />
						</q-card-section>
						<q-card-section>
							<div class="text-h6">问诊互动</div>
							<div class="text-caption">问诊交互界面</div>
						</q-card-section>
					</q-card>
				</div>
				
				<div class="col-12 col-sm-6 col-md-3">
					<q-card class="text-center q-pa-md" clickable @click="$router.push({ name: 'app.small.casebook' })">
						<q-card-section>
							<q-icon name="smartphone" size="4rem" color="accent" />
						</q-card-section>
						<q-card-section>
							<div class="text-h6">病例(移动端)</div>
							<div class="text-caption">移动端病例查看</div>
						</q-card-section>
					</q-card>
				</div>
				
				<div class="col-12 col-sm-6 col-md-3">
					<q-card class="text-center q-pa-md" clickable @click="$router.push({ name: 'app.large.casebook' })">
						<q-card-section>
							<q-icon name="desktop_windows" size="4rem" color="positive" />
						</q-card-section>
						<q-card-section>
							<div class="text-h6">病例(医生端)</div>
							<div class="text-caption">医生端病例查看</div>
						</q-card-section>
					</q-card>
				</div>
			</div>
		</div>
	</q-page>
</template>

<script setup lang="ts"></script>
