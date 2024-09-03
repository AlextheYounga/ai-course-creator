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
			<div class="float-right pb-4" v-if="this.nextPage">
				<a :href="this.nextPage"
				   class="ml-3 inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
					Next Page
				</a>
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
			nextPage: ''
		}
	},
	methods: {
		highlightCodeBlocks() {
			document.querySelectorAll('pre code').forEach((block) => {
				const parent = block.parentElement
				const secondParent = parent.parentElement
				const isCodepen = secondParent.classList.contains('codepen') || parent.classList.contains('codepen')

				if (!isCodepen) {
					hljs.highlightElement(block);
				}
			});
		},
		async getNextPage() {
			if (!this.nextPage) {
				const res = await fastApi.get(`/pages/${this.page.id}/next`)
				if (!res.data) return;
				this.nextPage = `/pages/${res.data}`
				console.log(this.nextPage)
			}
		}
	},
	computed: {
		pageHtml() {
			return this.page ? this.page.content : '';
		}
	},
	updated() {
		this.highlightCodeBlocks()
		this.getNextPage()
	},
	async beforeCreate() {
		// Get page
		if (!this.page) {
			const pageId = (this.$route.params.id)
			const res = await fastApi.get(`/pages/${pageId}`)
			this.page = res.data
		}
	}
}
</script>