// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

const base = process.env.NODE_ENV === 'production' ? '/starlight' : '';

// https://astro.build/config
export default defineConfig({
	site: 'https://vinayaksinghop89-maker.github.io',
	...(base ? { base } : {}),
	integrations: [
		starlight({
			title: 'AURA Robotics Lab',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/vinayaksinghop89-maker/starlight' }],
			sidebar: [
				{
					label: 'AURA',
					items: [
						{ label: '3D Tag Arena', link: `${base}/aura/` },
					],
				},
			],
		}),
	],
});
