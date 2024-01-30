<template>
    <div class="px-6 py-32 lg:px-8">
        <router-link to="/" class="rounded-md bg-red-800 px-2.5 py-1.5 text-sm font-semibold text-gray-200 shadow-sm hover:bg-white/20">&#8592; Back to Dashboard</router-link>
        <div class="mx-auto max-w-3xl text-base leading-7 text-gray-200">
            <div v-if="pageHtml" id="page-body">
                <div v-html="pageHtml"></div>
            </div>
        </div>
    </div>
</template>
  
<script lang="ts">
import flaskApi from '@/router/api'

export default {
    name: 'PageView',
    data() {
        const pageHtml: string = "";

        return {
            pageHtml: pageHtml,
        }
    },

    async beforeCreate() {
        const pageId = (this.$route.params.id as string)
        const pageContent = await flaskApi.get(`/page/${pageId}`)

        this.pageHtml = pageContent
    }
}
</script>