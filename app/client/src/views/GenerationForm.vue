<template>
	<div class="container mx-auto p-4">
		<Breadcrumbs />
	</div>

	<div class="container mx-auto px-4 sm:px-6 max-w-2xl py-12">
		<form>
			<div class="space-y-12">
				<div class="border-b border-white/10 pb-12">
					<h2 class="text-base font-semibold leading-7 text-white">Run New Generation</h2>
					<p class="mt-1 text-sm leading-6 text-gray-400">This information will be displayed publicly so be careful what you share.</p>

					<div class="mt-8">
						<RadioGroup v-model="form.selectedJob">
							<RadioGroupLabel class="text-base font-semibold leading-6 text-white">Select a Task</RadioGroupLabel>
							<div class="mt-4 grid grid-cols-1 gap-y-6 sm:grid-cols-3 sm:gap-x-4">
								<RadioGroupOption as="template" v-for="(description, task) in tasks" :key="task" :value="task" v-slot="{ active, checked }">
									<div :class="[active ? 'border-indigo-600 ring-2 ring-indigo-600' : 'border-white/10', 'relative flex cursor-pointer rounded-lg border bg-white/5 p-4 shadow-sm focus:outline-none']">
										<span class="flex flex-1">
											<span class="flex flex-col">
												<RadioGroupLabel as="span" class="block text-md font-semibold text-white">{{ task }}</RadioGroupLabel>
												<RadioGroupDescription as="span" class="mt-1 flex items-center text-sm text-gray-300">{{ description }}</RadioGroupDescription>
											</span>
										</span>
										<CheckCircleIcon :class="[!checked ? 'invisible' : '', 'h-5 w-5 text-indigo-600']" aria-hidden="true" />
										<span :class="[active ? 'border' : 'border-2', checked ? 'border-indigo-600' : 'border-transparent', 'pointer-events-none absolute -inset-px rounded-lg']" aria-hidden="true" />
									</div>
								</RadioGroupOption>
							</div>
						</RadioGroup>
					</div>

					<div v-if="!resumeJob" class="my-6">
						<label class="block text-sm font-medium leading-6 text-gray-200">
							<span>Topic</span>
							<select v-model="form.topicId" class="w-full flex rounded-md bg-white/5 ring-1 ring-inset ring-white/10 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500">
								<option value="">Select a Topic</option>
								<option v-for="topic in this.topics" :key="`topic-${topic.id}`" :value="topic.id">{{ topic.name }}</option>
							</select>
						</label>
					</div>

					<div v-if="generateContent">
						<div v-if="form.topicId" class="my-6">
							<label class="block text-sm font-medium leading-6 text-gray-200">
								<span>Outline *</span>
								<select v-model="form.outlineId" class="w-full flex rounded-md bg-white/5 ring-1 ring-inset ring-white/10 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500">
									<option value="">Select an Outline</option>
									<option v-for="outline in getTopicOutlines(form.topicId)" :key="outline.id" :value="outline.id">{{ outline.name }}</option>
								</select>
							</label>
						</div>

						<div class="flex justify-between my-6 items-center">
							<div class="w-1/2 mr-4">
								<label class="text-sm font-medium leading-6 text-gray-200">
									<span class="text-gray-200">Content Type to Generate *</span>
									<select v-model="form.contentType" class="w-full flex rounded-md bg-white/5 ring-1 ring-inset ring-white/10 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500">
										<option v-for="contentType in contentTypes" :key="contentType" :value="contentType">{{ contentType }}</option>
									</select>
								</label>
							</div>

							<div class="w-1/2">
								<span class="text-gray-200">Generate From Hierarchy Level *</span>
								<select v-model="form.entityType" class="w-full flex rounded-md bg-white/5 ring-1 ring-inset ring-white/10 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500">
									<option v-for="entityType in entityTypes" :key="entityType" :value="entityType">{{ entityType }}</option>
								</select>
							</div>
						</div>

						<div v-if="this.entities.length">
							<div class="my-6">
								<label class=" text-sm font-medium leading-6 text-gray-200">
									<span class="text-gray-200">Select an Outline Item to Generate</span>
									<select v-model="form.outlineIdEntityId" class="w-full flex rounded-md bg-white/5 ring-1 ring-inset ring-white/10 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500">
										<option value="">Select an Outline Entity to Generate</option>
										<option v-for="entity in this.entities" :key="`entity-${entity.id}`" :value="entity.id">{{ entity.name }}</option>
									</select>
								</label>
							</div>
						</div>
					</div>

					<div v-if="generateOutline || generateContent">
						<div class="flex justify-between my-6 items-center">
							<div class="w-1/3 mr-4">
								<label class="text-sm font-medium leading-6 text-gray-200">
									<span>Prompt Collection</span>
									<select v-model="form.promptCollection" class="w-full flex rounded-md bg-white/5 ring-1 ring-inset ring-white/10 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500">
										<option v-for="prompt in promptCollections" :key="prompt" :value="prompt">{{ capitalize(prompt) }}</option>
									</select>
								</label>
							</div>

							<div class="w-2/3">
								<label class="text-sm font-medium leading-6 text-gray-200">Language</label>
								<input v-model="form.language" class="w-full flex rounded-md bg-white/5 ring-1 ring-inset ring-white/10 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500" />
							</div>
						</div>
					</div>

					<div v-if="resumeJob" class="my-6">
						<label class="block text-sm font-medium leading-6 text-gray-200">
							<span>Job</span>
							<select v-model="form.jobId" class="w-full flex rounded-md bg-white/5 ring-1 ring-inset ring-white/10 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500">
								<option value="">Select a Job</option>
								<option v-for="job in this.jobs" :key="job.id" :value="job.id">{{ job.name }} - {{ job.created_at }}</option>
							</select>
						</label>
					</div>
				</div>

				<div v-if="generateContent" class="border-b border-white/10">
					<h3 class="text-base font-semibold leading-7 text-white pb-4">Component Settings</h3>
					<div class="space-y-12 pb-12">

						<fieldset>
							<legend class="text-base font-semibold leading-6 text-gray-400">Allow Interactives</legend>
							<div class="mt-1">
								<div v-for="interactive in ['multipleChoice','codeEditor', 'codepen']" :key="`settings-${interactive}`" class="relative flex items-start py-1">
									<div class="min-w-0 flex-1 text-sm leading-6">
										<label :for="`settings-${interactive}`" class="select-none font-medium text-white">{{ interactive }}</label>
									</div>
									<div class="ml-3 flex h-6 items-center">
										<input v-model="form.settings[interactive]" :id="`settings-${interactive}`" :name="`settings-${interactive}`" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600" />
									</div>
								</div>
							</div>
						</fieldset>

						<fieldset>
							<legend class="text-base font-semibold leading-6 text-gray-400">Interactives Per Page</legend>
							<div class="mt-1">
								<div class="relative flex items-start my-3">
									<div class="min-w-0 flex-1 text-sm leading-6">
										<label for="settings-counts-lesson" class="select-none font-medium text-white">Lesson</label>
									</div>
									<div class="ml-3 flex h-6 items-center text-black">
										<input v-model="form.settings.counts.lesson" id="settings-counts-lesson" name="settings-counts-lesson" type="number" min="1" max="30" class="text-xs rounded text-black my-2" />
									</div>
								</div>

								<div class="relative flex items-start my-3">
									<div class="min-w-0 flex-1 text-sm leading-6">
										<label for="settings-counts-challenge" class="select-none font-medium text-white">Practice Challenges</label>
									</div>
									<div class="ml-3 flex h-6 items-center text-black">
										<input v-model="form.settings.counts.challenge" id="settings-counts-challenge" name="settings-counts-challenge" type="number" min="1" max="30" class="text-xs rounded text-black my-2" />
									</div>
								</div>

								<div class="relative flex items-start my-3">
									<div class="min-w-0 flex-1 text-sm leading-6">
										<label for="settings-counts-fsc" class="select-none font-medium text-white">Final Skill Challenge</label>
									</div>
									<div class="ml-3 flex h-6 items-center text-black">
										<input v-model="form.settings.counts.finalSkillChallenge" id="settings-counts-fsc" name="settings-counts-fsc" type="number" min="1" max="30" class="text-xs rounded text-black my-2" />
									</div>
								</div>
							</div>
						</fieldset>

						<fieldset>
							<legend class="text-base font-semibold leading-6 text-gray-400">Interactives Weights</legend>
							<div class="mt-1">
								<div v-for="interactive in ['multipleChoice','codeEditor', 'codepen']" :key="`settings-${setting}`" class="relative flex items-start my-3">
									<div class="min-w-0 flex-1 text-sm leading-6">
										<label :for="`settings-weights-${interactive}`" class="select-none font-medium text-white">{{ interactive }}</label>
									</div>
									<div class="ml-3 flex h-6 items-center text-black">
										<input v-model="form.settings.weights[interactive]" :id="`settings-weights-${interactive}`" :name="`settings-weights-${interactive}`" type="number" min="0.1" max="1" class="text-xs rounded text-black my-2" />
									</div>
								</div>
							</div>
						</fieldset>
					</div>
				</div>
			</div>

			<div class="mt-12 flex items-center justify-end gap-x-6">
				<button type="button" class="text-sm font-semibold leading-6 text-white">Cancel</button>
				<button type="submit"
						class="rounded-md bg-indigo-500 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
					Run
				</button>
			</div>
		</form>
	</div>
</template>

<script>
import { ref } from 'vue'
import { capitalize } from '@/helpers/index'
import { RadioGroup, RadioGroupDescription, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue'
import { CheckCircleIcon } from '@heroicons/vue/20/solid'
import fastApi from '@/router/api'
import Breadcrumbs from '@/components/Breadcrumbs.vue'

const tasks = {
	'Generate Outline': 'Generate an outline for a new topic',
	'Generate Content': 'Generate content for a new topic',
	'Resume Job': 'Resume an existing job'
}

const promptCollections = [
	'core',
	'programming',
	'practical',
	'intellectual',
]

const entityTypes = [
	'Topic',
	'Course',
	'Chapter',
	'Page',
]

const contentTypes = [
	'Lesson Content',
	'Lesson Content and Interactives',
	'Interactives'
]


const form = ref({
	jobId: null,
	topicId: null,
	outlineId: null,
	outlineEntityId: null,
	promptCollection: 'default',
	language: null,
	selectedJob: null,
	entityType: 'Topic',
	contentType: null,
	settings: {
		multipleChoice: true,
		codeEditor: true,
		codepen: false,
		counts: {
			lesson: 1,
			challenge: 5,
			finalSkillChallenge: 20
		},
		weights: {
			multipleChoice: 0.6,
			codeEditor: 0.2,
			codepen: 0.2
		}
	}
});

// console.log(form.)
// for (const p of Object.keys(form.settings.counts)) {
// 	console.log(form.settings.counts[p])
// }

export default {
	name: 'GenerationForm',
	components: {
		Breadcrumbs,
		RadioGroup, RadioGroupDescription, RadioGroupLabel, RadioGroupOption,
		CheckCircleIcon
	},
	setup() {
		return {
			form,
			tasks,
			promptCollections,
			entityTypes,
			contentTypes,
			capitalize
		}
	},
	data() {
		return {
			topics: [],
			jobs: [],
			entities: []
		}
	},
	methods: {
		async getTopics() {
			const res = await fastApi.get('/topics')
			this.$data.topics = res.data
		},
		async getStartedJobs() {
			const res = await fastApi.get('/jobs')
			const jobRecords = res.data
			const activeJobs = jobRecords.filter(job => job.status === 'started')
			this.$data.jobs = activeJobs
		},
		async getOutlineEntities(entityType) {
			const outlineId = this.form.outlineId
			const res = await fastApi.get(`/outline/${outlineId}/entities/${entityType}`)
			this.entities = res.data
		},
		getTopicOutlines(id) {
			return this.topics.find(topic => topic.id === id).outlines
		},
		onSubmit() {
			localStorage.setItem('generate-form', JSON.stringify(data));
		}
	},
	watch: {
		'form.entityType': {
			handler: async function (entityType) {
				if (this.form.outlineId) {
					await this.getOutlineEntities(entityType)
				}
			}
		}
	},
	computed: {
		generateOutline() {
			return this.form.selectedJob === 'Generate Outline'
		},
		generateContent() {
			return this.form.selectedJob === 'Generate Content'
		},
		resumeJob() {
			return this.form.selectedJob === 'Resume Job'
		},
	},
	beforeCreate() {
		const data = localStorage.getItem('generate-form');
		if (data) {
			this.form = JSON.parse(data);
		}
	},
	mounted() {
		this.getTopics()
		this.getStartedJobs()
	}
}

</script>