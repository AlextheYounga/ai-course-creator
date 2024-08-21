<template>
	<div class="lg:px-8">
		<div class="flex py-4 justify-between">
			<Breadcrumbs />

			<SwitchGroup as="div" class="flex items-center">
				<Switch v-model="challenges"
						:class="[challenges ? 'bg-amber-600' : 'bg-gray-200', 'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-amber-600 focus:ring-offset-2']">
					<span aria-hidden="true" :class="[challenges ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out']" />
				</Switch>
				<SwitchLabel as="span" class="ml-3 mr-3 text-sm">
					<span class="font-medium">Show Challenges</span>
				</SwitchLabel>
			</SwitchGroup>
		</div>

		<div class="flex">
			<div class="mx-auto max-w-3xl text-base leading-7 text-gray-200">
				<div v-for="page of this.course.pages">
					<div id="page-body">
						<div v-html="page.content"></div>

						<div v-if="pageInteractives(page)" id="interactives">
							<div v-for="interactive in pageInteractives(page)">
								<template v-if="interactive.type == 'codeEditor'">
									<CodeEditor :interactive=interactive></CodeEditor>
								</template>
								<!-- <template v-if="interactive.type == 'codepen'">
									<Codepen :data=interactive></Codepen>
								</template>
								<template v-else-if="interactive.type == 'codeEditor'">
									<CodeEditor :interactive=interactive></CodeEditor>
								</template>
								<template v-else-if="interactive.type == 'multipleChoice'">
									<MultipleChoice :data=interactive></MultipleChoice>
								</template>
								<template v-else-if="interactive.type == 'fillBlank'">
									<FillInTheBlank :data=interactive></FillInTheBlank>
								</template> -->
							</div>
						</div>
					</div>
				</div>
			</div>
			<div v-if="courseHtml">
				<AnchorNavigation :htmlContent="courseHtml" />
			</div>
		</div>
	</div>
</template>


<script>
import { ref } from 'vue'
import { Switch, SwitchGroup, SwitchLabel } from '@headlessui/vue'
import hljs from 'highlight.js';
import fastApi from '@/router/api'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import AnchorNavigation from '@/components/AnchorNavigation.vue'
import CodeEditor from '@/components/Interactives/CodeEditor.vue'
import Codepen from '@/components/Interactives/Codepen.vue'
import FillInTheBlank from '@/components/Interactives/FillInTheBlank.vue'
import MultipleChoice from '@/components/Interactives/MultipleChoice.vue'


export default {
	name: 'CourseView',
	components: {
		AnchorNavigation,
		Breadcrumbs,
		Switch, SwitchGroup, SwitchLabel,
		CodeEditor, Codepen, FillInTheBlank, MultipleChoice
	},
	data() {
		return {
			challenges: ref(true),
			course: {}
		}
	},
	methods: {
		pageInteractives(page) {
			if (this.challenges == false) return []
			return page.interactives
		}
	},
	computed: {
		courseHtml() {
			if (!this.course?.pages) return ''
			return this.course.pages.map(page => page.content).join('\n\n')
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
		const courseId = (this.$route.params.id)
		const res = await fastApi.get(`/courses/${courseId}`)
		this.course = res.data
	},
}
</script>

<style scoped>
#page-body {
	margin: 5rem 0;
	padding-bottom: 5rem;
	border-bottom: 1px solid #44403c
}
</style>
