<template>
    <div class="lg:px-8">
        <div class="flex py-4 justify-between mb-16">
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
                <div v-if="courseHtml" id="page-body">
                    <div v-html="courseHtml"></div>
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
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import flaskApi from '@/router/api'
import AnchorNavigation from '@/components/AnchorNavigation.vue'
import hljs from 'highlight.js';

export default {
    name: 'CourseContent',
    components: {
        AnchorNavigation,
        Breadcrumbs,
        Switch, SwitchGroup, SwitchLabel
    },
    data() {
        const courseHtml = "";

        return {
            challenges: ref(false),
            courseHtml: courseHtml,
            courseContent: [],
        }
    },
    methods: {
        compileCourseHtml(courseContent) {
            let html = ""
            for (const page of courseContent) {
                if (this.challenges == false && page.type.includes('challenge')) {
                    continue
                }

                const pageHtml = `\n\n<div style="margin:5rem 0;" class="page">` + page.html + "</div>\n\n"
                const formattedHtml = pageHtml.replace(/<h1/g, '<h2').replace(/<\/h1/g, '</h2')
                html += formattedHtml
            }
            return html
        }
    },
    watch: {
        challenges: {
            immediate: true,
            handler() {
                this.courseHtml = this.compileCourseHtml(this.courseContent)
            }
        }
    },
    updated() {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    },
    async beforeCreate() {
        const courseId = (this.$route.params.id)
        this.courseContent = await flaskApi.get(`/courses/${courseId}/content`)

        this.courseHtml = this.compileCourseHtml(this.courseContent)
    },
}
</script>

<style>
.page {
    margin: 5rem 0;
    padding-bottom: 5rem;
    border-bottom: 1px solid #44403c
}

/* Temporary */
[id^="answerable"] {
    display: none;
}
</style>