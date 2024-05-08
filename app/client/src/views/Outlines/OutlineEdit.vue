<template>
    <div class="container mx-auto">
        <div class="py-4">
            <Breadcrumbs />
        </div>


        <div class="px-6 pt-12 lg:px-8">
            <h1 class="text-3xl font-semibold leading-7 text-white">Outline</h1>
            <div class="mx-auto text-base leading-7 text-gray-200">
                <div v-if="stats">
                    <div class="bg-gray-900 py-8">
                        <div class="mx-auto px-6 lg:px-8">
                            <div class="mx-auto max-w-2xl lg:max-w-none">
                                <dl class="grid grid-cols-1 gap-0.5 overflow-hidden rounded-2xl text-center sm:grid-cols-2 lg:grid-cols-4">
                                    <div v-for="stat in stats" :key="stat.id" class="flex flex-col bg-white/5 p-6">
                                        <dt class="text-sm font-semibold leading-6 text-gray-300">{{ stat.name }}</dt>
                                        <dd class="truncate order-first text-lg font-semibold tracking-tight text-white">{{ stat.value }}</dd>
                                    </div>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                <textarea rows="20" v-model="outlineYaml"
                    class="block w-full rounded-md border-0 bg-white/5 py-1.5 text-white shadow-sm ring-1 ring-inset ring-white/10 focus:ring-2 focus:ring-inset focus:ring-indigo-500 text-base sm:leading-6" />

                <button v-show="showButton" @click="submit"
                type="button"
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
    name: 'OutlineEdit',
    components: { Breadcrumbs },
    data() {
        return {
            outline: null,
            outlineYaml: '',
        }
    },
    methods: {
        async submit() {
            const data = {
                ...this.outline,
                outlineData: YAML.parse(this.outlineYaml)
            }

            await fastApi.post(`/outlines`, data)
            alert('Outline Created Successfully')
        },
        async getOutline() {
            const outlineId = (this.$route.params.id)
            const res = await fastApi.get(`/outlines/${outlineId}`)
            this.outline = res.data
            this.outlineYaml = YAML.stringify(outline?.outline_data, { indent: 4 }) ?? ''
        },
    },
    computed: {
        stats() {
            return [
                { id: 1, name: 'Outline ID', value: this.outline?.id },
                { id: 2, name: 'Outline Name', value: this.outline?.name },
                { id: 3, name: 'Course Count', value: this.outline?.outline_data?.length ?? 'NA' },
                { id: 4, name: 'Created At', value: this.outline?.created_at },
            ]
        },
        showButton() {
            if (this.outlineYaml) {
                const dataOutput = YAML.parse(this.outlineYaml)
                return JSON.stringify(dataOutput) !== JSON.stringify(this.outline.outline_data)
            }
            return false;
        }
    },
    mounted() {
        this.getOutline()
    }
}
</script>