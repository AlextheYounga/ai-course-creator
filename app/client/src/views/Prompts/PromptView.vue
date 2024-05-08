<template>
    <div class="container mx-auto">
        <div class="py-4">
            <Breadcrumbs />
        </div>
        
        <div class="px-4 sm:px-0 my-12">
            <h1 class="text-3xl font-semibold leading-7 text-white">Prompt & Response Details</h1>
        </div>

        <div>
            <div class="block">
                <div class="border-b border-gray-400">
                    <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                        <a v-for="tab in tabs" :key="tab.name" :href="tab.href" @click="selectTab(tab)"
                            :class="[tab.current ? 'border-cyan-500 text-cyan-600' : 'border-transparent text-gray-300 hover:border-gray-300 hover:text-gray-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']"
                            :aria-current="tab.current ? 'page' : undefined">{{ tab.name }}
                        </a>
                    </nav>
                </div>
            </div>
        </div>

        <div class="mt-3">
            <h3 class="text-2xl mt-12 mb-2 font-bold text-gray-100">{{ tabData.name }}</h3>
            <dl v-if="log && tabData" class="divide-y divide-white/10">
                <div v-for="property in Object.keys(tabData.data)" class="px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-0">
                    <dt class="text-sm font-medium leading-6 text-white">{{ property }}</dt>

                    <dd v-if="property == 'content'" class="mt-1 text-sm leading-6 text-gray-200 sm:col-span-2 sm:mt-0">
                        <textarea rows="12" :value="tabData.data[property]" disabled class="block w-full rounded-md border-0 bg-white/5 py-1.5 text-white shadow-sm ring-1 ring-inset ring-white/10 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm sm:leading-6" />
                    </dd>

                    <dd v-else-if="property == 'properties' || property == 'payload'" class="mt-1 text-sm sm:col-span-2 sm:ml-6 sm:mt-0 block overflow-x-scroll">
                        <code class="language-json">
                            <pre class="bg-black text-gray-200 overflow-x-scroll p-4">{{ getJsonField(tabData.data[property]) }}</pre>
                        </code>
                    </dd>

                    <dd v-else class="mt-1 text-sm leading-6 text-gray-200 sm:col-span-2 sm:mt-0">{{ tabData.data[property] }}</dd>
                </div>
            </dl>
        </div>
    </div>
</template>
  
<script>
import fastApi from '@/router/api'
import {
    Dialog,
    DialogPanel,
    DialogTitle,
    Menu,
    MenuButton,
    MenuItem,
    MenuItems,
    TransitionChild,
    TransitionRoot,
} from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { EllipsisVerticalIcon } from '@heroicons/vue/20/solid'
import Breadcrumbs from '@/components/Breadcrumbs.vue'


export default {
    name: 'PromptView',
    components: {
        Dialog,
        DialogPanel,
        DialogTitle,
        Menu,
        MenuButton,
        MenuItem,
        MenuItems,
        TransitionChild,
        TransitionRoot,
        XMarkIcon,
        EllipsisVerticalIcon,
        Breadcrumbs
    },
    data() {
        const log = undefined;
        const logItems = ['prompt', 'response']
        const tabs = [
            { name: 'Prompt', href: '#prompt', current: true },
            { name: 'Response', href: '#response', current: false },
        ]

        return {
            tabs,
            log,
            logItems
        }
    },
    methods: {
        getTabSelected() {
            return this.tabs.find(tab => tab.current)
        },
        getJsonField(jsonField) {
            return JSON.stringify(jsonField, null, 4).trim()
        },
        selectTab(tab) {
            this.tabs.forEach((t) => {
                if (t.name === tab.name) {
                    t.current = true
                } else {
                    t.current = false
                }
            })
        }
    },
    computed: {
        tabData() {
            const tab = this.getTabSelected()
            if (!this.log || !tab) return {}
            return { name: tab.name, data: this.log[tab.name.toLowerCase()] }
        }
    },

    async mounted() {
        const promptId = (this.$route.params.id)
        const res = await fastApi.get(`/prompts/${promptId}`)
        this.log = res.data
    }
}
</script>