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
                <div v-for="page of coursePages">
                    <div id="page-body">
                        <div v-for="node of page.nodes">
                            <template v-if="node.type == 'html'">
                                <div v-html="node.content"></div>
                            </template>
                            <template v-else-if="node.type == 'codepen'">
                                <Codepen :data=node></Codepen>
                            </template>
                            <template v-else-if="node.type == 'codeEditor'">
                                <CodeEditor :data=node></CodeEditor>
                            </template>
                            <template v-else-if="node.type == 'multipleChoice'">
                                <MultipleChoice :data=node></MultipleChoice>
                            </template>
                            <template v-else-if="node.type == 'fillBlank'">
                                <FillInTheBlank :data=node></FillInTheBlank>
                            </template>
                            <template v-else>
                                <div v-html="node?.content"></div>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
            <div v-if="courseHtml">
                <AnchorNavigation :key="courseHtml" :htmlContent="courseHtml" />
            </div>
        </div>
    </div>
</template>


<script>
import { ref } from 'vue'
import { Switch, SwitchGroup, SwitchLabel } from '@headlessui/vue'
import hljs from 'highlight.js';
import flaskApi from '@/router/api'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import AnchorNavigation from '@/components/AnchorNavigation.vue'
import CodeEditor from '@/components/Interactives/CodeEditor.vue'
import Codepen from '@/components/Interactives/Codepen.vue'
import FillInTheBlank from '@/components/Interactives/FillInTheBlank.vue'
import MultipleChoice from '@/components/Interactives/MultipleChoice.vue'


export default {
    name: 'CourseContent',
    components: {
        AnchorNavigation,
        Breadcrumbs,
        Switch, SwitchGroup, SwitchLabel,
        CodeEditor, Codepen, FillInTheBlank, MultipleChoice
    },
    data() {
        return {
            challenges: ref(false),
            courseContent: []
        }
    },
    methods: {
        processNodes(courseContent) {
            const content = []
            for (const page of courseContent) {
                if (this.challenges == false && page.type.includes('challenge')) {
                    continue
                }
                content.push(page)
            }
            return content
        }
    },
    updated() {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    },
    computed: {
        coursePages() {
            if (this.courseContent.length) {
                return this.processNodes(this.courseContent)
            }
            return []
        }
    },
    async beforeCreate() {
        const courseId = (this.$route.params.id)
        this.courseContent = await flaskApi.get(`/courses/${courseId}/content`)
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

