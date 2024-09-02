<template>
	<div class="p-4">
		<Breadcrumbs />
	</div>

	<div class="flex justify-end">
		<div class="mx-auto max-w-3xl text-base leading-7 text-gray-200">
			<div v-if="this.page" id="page-body">
				<div v-html="pageHtml"></div>

				<div v-if="this.page.interactives" id="interactives">
					<div v-for="interactive in this.page.interactives">
						<template v-if="interactive.type == 'codeEditor'">
							<CodeEditor :interactive=interactive></CodeEditor>
						</template>
						<template v-else-if="interactive.type == 'codepen'">
							<Codepen :interactive=interactive></Codepen>
						</template>
						<template v-else-if="interactive.type == 'multipleChoice'">
							<MultipleChoice :interactive=interactive></MultipleChoice>
						</template>
						<template v-else-if="interactive.type == 'fillBlank'">
							<FillInTheBlank :interactive=interactive></FillInTheBlank>
						</template>
					</div>
				</div>
			</div>
		</div>
		<div class="hidden 2xl:flex w-1/4" v-if="this.page">
			<AnchorNavigation :htmlContent="pageHtml" />
		</div>
	</div>
</template>

<script>
import hljs from 'highlight.js';
import fastApi from '@/router/api'
import AnchorNavigation from '@/components/AnchorNavigation.vue'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import CodeEditor from '@/components/Interactives/CodeEditor.vue'
import Codepen from '@/components/Interactives/Codepen.vue'
import FillInTheBlank from '@/components/Interactives/FillInTheBlank.vue'
import MultipleChoice from '@/components/Interactives/MultipleChoice.vue'

export default {
	name: 'PageView',
	components: {
		Breadcrumbs,
		AnchorNavigation,
		CodeEditor, Codepen, FillInTheBlank, MultipleChoice
	},
	data() {
		return {
			page: undefined,
		}
	},
	computed: {
		pageHtml() {
			return this.page ? this.page.content : '';
		}
	},
	updated() {
		document.querySelectorAll('pre code').forEach((block) => {
			const parent = block.parentElement
			const secondParent = parent.parentElement
			const isCodepen = secondParent.classList.contains('codepen') || parent.classList.contains('codepen')

			if (!isCodepen) {
				hljs.highlightElement(block);
			}
		});
	},
	async beforeCreate() {
		const pageId = (this.$route.params.id)
		const res = await fastApi.get(`/pages/${pageId}`)
		this.page = res.data
	}
}
</script>