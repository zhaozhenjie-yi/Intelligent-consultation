import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
	{
		path: '/',
		component: () => import('layouts/MainLayout.vue'),
		children: [{
			name: 'app.index',
			path: '',
			component: () => import('pages/IndexPage.vue'),
		}],
	},

	{
		name: 'app.small.casebook',
		path: '/casebook/small',
		component: () => import('pages/SmallCasebook/Page.vue'),
	},
	{
		name: 'app.interaction',
		path: '/interaction',
		component: () => import('pages/Interaction/Page.vue'),
		// The URL format /?uid={uid}#/interaction is handled via route.query.uid in the component
	},
	// 添加新的URL格式路由 - 用于支持 /#?uid={uid}/interaction 格式
	// 在Vue Router中无法直接处理hash之后的内容，所以将在组件内部解析
	{
		name: 'app.large.casebook',
		path: '/casebook/large',
		component: () => import('pages/LargeCasebook/Page.vue'),
	},
	{
		name: 'app.patient.management',
		path: '/patient-management',
		component: () => import('pages/PatientManagement/Page.vue'),
	},

	// Always leave this as last one,
	// but you can also remove it
	{
		path: '/:catchAll(.*)*',
		component: () => import('pages/ErrorNotFound.vue'),
	},
];

export default routes;
