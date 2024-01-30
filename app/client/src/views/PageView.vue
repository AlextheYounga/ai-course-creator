<template>
    <div class="px-6 py-32 lg:px-8">
        <div class="mx-auto max-w-3xl text-base leading-7 text-gray-700">
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
        const pageHtml = null;
        const pageId = this.$route.params.id;
        return {
            pageHtml,
            pageId
        }
    },

    async beforeCreate() {
        const pageContent = await flaskApi.get(`/page/${this.pageId}`)
        this.pageHtml = pageContent.data.html
    }
}
</script>