<template>
    <div class="p-4">
        <Breadcrumbs />
    </div>
    <div class="px-6 py-16 lg:px-8">
        <div class="mx-auto max-w-3xl text-base leading-7 text-gray-200">
            <div v-if="pageHtml" id="page-body">
                <div v-html="pageHtml"></div>
            </div>
        </div>
    </div>
</template>

<script>
import hljs from 'highlight.js';
import flaskApi from '@/router/api'
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
    name: 'PageView',
    components: {
        Breadcrumbs
    },
    data() {
        const pageHtml = "";

        return {
            pageHtml: pageHtml,
        }
    },
    updated() {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    },
    async beforeCreate() {
        const pageId = (this.$route.params.id)
        const pageContent = await flaskApi.get(`/pages/${pageId}`)

        this.pageHtml = pageContent
    }
}
</script>