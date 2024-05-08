<template>
    <div class="p-4">
        <Breadcrumbs />
    </div>
    <div class="px-6 py-16 lg:px-8">
        <div class="mx-auto max-w-3xl text-base leading-7 text-gray-200">
            <div v-if="nodes">
                <div id="page-body">
                    <div v-for="node of nodes">
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
    </div>
</template>

<script>
import hljs from 'highlight.js';
import fastApi from '@/router/api'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import CodeEditor from '@/components/Interactives/CodeEditor.vue'
import Codepen from '@/components/Interactives/Codepen.vue'
import FillInTheBlank from '@/components/Interactives/FillInTheBlank.vue'
import MultipleChoice from '@/components/Interactives/MultipleChoice.vue'

export default {
    name: 'PageView',
    components: {
        Breadcrumbs,
        CodeEditor, Codepen, FillInTheBlank, MultipleChoice
    },
    data() {
        return {
            page: undefined,
            nodes: []
        }
    },
    updated() {
        document.querySelectorAll('pre code').forEach((block) => {
            const parent = block.parentElement
            const secondParent = parent.parentElement
            const isCodepen = secondParent.classList.contains('codepen') || parent.classList.contains('codepen')
            
            if (isCodepen) {
                hljs.highlightElement(block);
            }
        });
    },
    async beforeCreate() {
        const pageId = (this.$route.params.id)
        const res = await fastApi.get(`/pages/${pageId}`)
        const page = res.data
        const nodes = page?.properties?.nodes ?? []

        this.page = page
        this.nodes = nodes
    }
}
</script>