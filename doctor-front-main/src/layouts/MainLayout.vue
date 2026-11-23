<template>
	<q-layout view="lHh Lpr lFf">
		<q-header elevated>
			<q-toolbar>
				<q-btn
					flat
					dense
					round
					icon="menu"
					aria-label="Menu"
					:to="{ name: 'app.index' }"
				/>

				<div class="q-ml-md">DoctorX 医疗系统</div>
				
				<q-space />
				
				<q-tabs>
					<q-route-tab to="/" label="首页" />
					<q-route-tab to="/patient-management" label="就诊人管理" />
					<q-route-tab to="/interaction" label="问诊交互" />
				</q-tabs>
			</q-toolbar>
		</q-header>

		<q-page-container>
			<router-view />
		</q-page-container>
	</q-layout>
</template>

<script setup lang="ts"></script>
