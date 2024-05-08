<template>
    <div class="container mx-auto">
        <div class="py-4">
            <Breadcrumbs />
        </div>


        <div class="px-6 pt-12 lg:px-8">
            <h1 class="text-3xl font-semibold leading-7 text-white">Outline</h1>
            <div class="mx-auto text-base leading-7 text-gray-200">

                <label class="block text-sm font-medium leading-6 text-gray-200 my-12">
                    <span>Topic</span>
                    <select v-model="topicId" class="w-full flex rounded-md bg-white/5 ring-1 ring-inset ring-white/10 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500">
                        <option value="">Select a Topic</option>
                        <option v-for="topic in topics" :key="`topic-${topic.id}`" :value="topic.id">{{ topic.name }}</option>
                    </select>
                </label>

                <textarea rows="20" v-model="outlineYaml" class="block w-full rounded-md border-0 bg-white/5 py-1.5 text-white shadow-sm ring-1 ring-inset ring-white/10 focus:ring-2 focus:ring-inset focus:ring-indigo-500 text-base sm:leading-6" />

                <button v-show="showButton" @click="submit" type="button"
                    class="float-right my-3 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                    Create New
                </button>
            </div>
        </div>
    </div>
</template>


<script>
import fastApi from '@/router/api'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import YAML from 'yaml'

export default {
    name: 'OutlineNew',
    components: { Breadcrumbs },
    
    data() {
        return {
            topics: [],
            topicId: null,
            outlineYaml: '',
        }
    },
    methods: {
        async submit() {
            const data = {
                topicId: this.topicId,
                outlineData: YAML.parse(this.outlineYaml)
            }

            await fastApi.post(`/outlines`, data)
            alert('Outline Created Successfully')
        },
        async getTopics() {
            const res = await fastApi.get('/topics')
            this.$data.topics = res.data
        },
    },
    computed: {
        showButton() {
            return typeof this.topicId === 'number' && this.outlineYaml !== ''
        }
    },
    mounted() {
        this.getTopics()
    }
}
</script>