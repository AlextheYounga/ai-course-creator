<template>
    <div>
        <TransitionRoot as="template" :show="sidebarOpen">
            <Dialog as="div" class="relative z-50 xl:hidden" @close="sidebarOpen = false">
                <TransitionChild as="template" enter="transition-opacity ease-linear duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="transition-opacity ease-linear duration-300" leave-from="opacity-100" leave-to="opacity-0">
                    <div class="fixed inset-0 bg-gray-900/80" />
                </TransitionChild>

                <div class="fixed inset-0 flex">
                    <TransitionChild as="template" enter="transition ease-in-out duration-300 transform" enter-from="-translate-x-full" enter-to="translate-x-0" leave="transition ease-in-out duration-300 transform" leave-from="translate-x-0"
                        leave-to="-translate-x-full">
                        <DialogPanel class="relative mr-16 flex w-full max-w-xs flex-1">
                            <TransitionChild as="template" enter="ease-in-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in-out duration-300" leave-from="opacity-100" leave-to="opacity-0">
                                <div class="absolute left-full top-0 flex w-16 justify-center pt-5">
                                    <button type="button" class="-m-2.5 p-2.5" @click="sidebarOpen = false">
                                        <span class="sr-only">Close sidebar</span>
                                        <XMarkIcon class="h-6 w-6 text-white" aria-hidden="true" />
                                    </button>
                                </div>
                            </TransitionChild>
                            <!-- Sidebar component, swap this element with another sidebar if you like -->
                            <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-gray-900 px-6 ring-1 ring-white/10">
                                <div class="flex h-16 shrink-0 items-center">
                                    <img class="h-8 w-auto" src="https://tailwindui.com/img/logos/mark.svg?color=indigo&shade=500" alt="Your Company" />
                                </div>
                                <nav class="flex flex-1 flex-col">
                                    <ul role="list" class="flex flex-1 flex-col gap-y-7">
                                        <li>
                                            <ul role="list" class="-mx-2 space-y-1">
                                                <li v-for="item in navigation" :key="item.name">
                                                    <router-link :to="item.href" class="text-gray-400 hover:text-white hover:bg-gray-800 group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold">
                                                        <component :is="item.icon" class="h-6 w-6 shrink-0" aria-hidden="true" />
                                                        {{ item.name }}
                                                    </router-link>
                                                </li>
                                            </ul>
                                        </li>
                                    </ul>
                                </nav>
                            </div>
                        </DialogPanel>
                    </TransitionChild>
                </div>
            </Dialog>
        </TransitionRoot>

        <!-- Static sidebar for desktop -->
        <div class="hidden xl:fixed xl:inset-y-0 xl:z-50 xl:flex xl:w-72 xl:flex-col">
            <!-- Sidebar component, swap this element with another sidebar if you like -->
            <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-black/10 px-6 ring-1 ring-white/5">
                <div class="flex h-16 shrink-0 items-center">
                    <img class="h-8 w-auto" src="https://tailwindui.com/img/logos/mark.svg?color=indigo&shade=500" alt="Your Company" />
                </div>
                <nav class="flex flex-1 flex-col">
                    <ul role="list" class="flex flex-1 flex-col gap-y-7">
                        <li>
                            <ul role="list" class="-mx-2 space-y-1">
                                <li v-for="item in navigation" :key="item.name">
                                    <router-link :to="item.href" class="text-gray-400 hover:text-white hover:bg-gray-800 group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold">
                                        <component :is="item.icon" class="h-6 w-6 shrink-0" aria-hidden="true" />
                                        {{ item.name }}
                                    </router-link>
                                </li>
                            </ul>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>

        <div class="xl:pl-72">
            <main>
                <header class="border-b border-white/5 px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
                    <div class="flex md:items-center justify-between">
                        <div class="min-w-0 flex-1">
                            <h1 class="text-2xl font-bold leading-7 text-white sm:truncate sm:text-3xl sm:tracking-tight">Course Creator</h1>
                        </div>
                        <div class="mt-4 flex md:ml-4 md:mt-0">
                            <router-link to="/generate"
                                class="ml-3 inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                                Run New Generation
                            </router-link>
                        </div>
                    </div>
                </header>

                <!-- Content -->
                <div v-if="!outlineGenerated" class="p-8">
                    <div>
                        <div class="flex flex-wrap gap-2 mb-4">
                            <button type="button" class="rounded-md bg-white/10 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-white/20" label="Expand All" @click="expandAll">Expand All</button>
                            <button type="button" class="rounded-md bg-white/10 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-white/20" label="Collapse All" @click="collapseAll">Collapse All</button>
                        </div>
                    </div>

                    <div>
                        <div class="h-72 p-4 flex justify-center">
                            <Tree v-model:expandedKeys="expandedKeys" class="w-full" :value="nodes">
                                <!-- Default Nodes -->
                                <template #default="slotProps">
                                    <div class="flex items-center overflow-y-visible">
                                        <component :is="slotProps.node?.data?.icon" class="h-6 w-6 shrink-0 pl-1" aria-hidden="true" />
                                        <p class="p-1">{{ slotProps.node.label }}</p>
                                        <Menu as="div" class="relative ml-auto">
                                            <MenuButton class="-m-2.5 block p-2.5 text-gray-400 hover:text-gray-500">
                                                <span class="sr-only">Open options</span>
                                                <EllipsisHorizontalIcon class="h-5 w-5" aria-hidden="true" />
                                            </MenuButton>
                                            <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
                                                leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
                                                <MenuItems class="absolute z-50 mt-0.5 bg-white origin-top-right rounded-md py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
                                                    <MenuItem v-slot="{ active }">
                                                    <button @click="generateFromNode(slotProps.node)" :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-xs leading-6 text-gray-800 text-nowrap']">
                                                        Generate {{ slotProps.node?.data?.entityType }}
                                                    </button>
                                                    </MenuItem>
                                                </MenuItems>
                                            </transition>
                                        </Menu>
                                    </div>
                                </template>
                                <!-- Page Nodes -->
                                <template #url="slotProps">
                                    <div class="flex items-center">
                                        <span class="flex items-center">
                                            <component :is="slotProps.node?.data?.icon" class="h-6 w-6 shrink-0 pl-1" aria-hidden="true" />
                                            <router-link class="p-1 text-blue-500" :to="slotProps.node?.data?.url ?? '#'">
                                                {{ slotProps.node.label }}
                                            </router-link>
                                        </span>
                                        <span class="p-2.5 items-center">
                                            <div v-if="slotProps.node?.data?.entityType == 'Page'" :class="[slotProps.node?.data?.exists ? 'text-green-400 bg-green-400/10' : 'text-rose-400 bg-rose-400/10', 'flex-none rounded-full p-1']">
                                                <div class="h-1.5 w-1.5 rounded-full bg-current"></div>
                                            </div>
                                        </span>
                                        <Menu as="div" class="relative ml-auto">
                                            <MenuButton class="-m-2.5 block p-2.5 text-gray-400 hover:text-gray-500">
                                                <span class="sr-only">Open options</span>
                                                <EllipsisHorizontalIcon class="h-5 w-5" aria-hidden="true" />
                                            </MenuButton>
                                            <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
                                                leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
                                                <MenuItems class="absolute z-50 mt-0.5 bg-white origin-top-right rounded-md py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
                                                    <MenuItem v-slot="{ active }">
                                                    <button @click="generateFromNode(slotProps.node)" :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-xs leading-6 text-gray-800 text-nowrap']">Generate {{ slotProps.node?.data?.entityType
                                                        }}</button>
                                                    </MenuItem>
                                                </MenuItems>
                                            </transition>
                                        </Menu>
                                    </div>
                                </template>
                            </Tree>
                        </div>
                    </div>
                </div>
                <div v-else>
                    <div>
                        <div class="px-6 py-24 sm:px-6 sm:py-32 lg:px-8">
                            <div class="mx-auto max-w-2xl text-center">
                                <h2 class="text-3xl font-bold tracking-tight text-white sm:text-4xl">Let's Learn Everything!</h2>
                                <div>
                                    <h3 class="mx-auto mt-6 max-w-xl text-lg leading-8 text-gray-300">Step 1: Add some topics</h3>
                                    <div class="mt-2 flex items-center justify-center gap-x-6">
                                        <router-link to="/topics"
                                            class="ml-3 inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                                            Add Topics
                                        </router-link>
                                    </div>
                                </div>

                                <div>
                                    <h3 class="mx-auto mt-6 max-w-xl text-lg leading-8 text-gray-300">Step 2: Generate Content</h3>
                                    <div class="mt-2 flex items-center justify-center gap-x-6">
                                        <router-link to="/generate"
                                            class="ml-3 inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                                            Run New Generation
                                        </router-link>
                                    </div>
                                </div>

                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import Tree from 'primevue/tree';
import {
    Dialog,
    DialogPanel,
    TransitionChild,
    TransitionRoot,
    Menu,
    MenuButton,
    MenuItem,
    MenuItems
} from '@headlessui/vue'
import {
    ServerIcon,
    XMarkIcon,
    FolderIcon,
    ListBulletIcon,
    LightBulbIcon,
} from '@heroicons/vue/24/outline';
import { EllipsisHorizontalIcon } from '@heroicons/vue/20/solid';
import fastApi from '@/router/api'
import { translateToTreeLibrary } from '@/helpers/tree-helpers'


export default {
    name: 'DashboardView',
    components: {
        Tree,
        Dialog,
        DialogPanel,
        TransitionChild,
        TransitionRoot,
        Menu,
        MenuButton,
        MenuItem,
        MenuItems,
        ServerIcon,
        XMarkIcon,
        FolderIcon,
        ListBulletIcon,
        LightBulbIcon,
        EllipsisHorizontalIcon,
    },
    data() {
        const nodes = ref([]);
        const expandedKeys = ref({});
        const selectedKey = ref(undefined);

        const navigation = [
            { name: 'Topics', href: '/topics', icon: LightBulbIcon, },
            { name: 'Outlines', href: '/outlines', icon: ListBulletIcon },
            { name: 'Prompt Logs', href: '/prompts', icon: ServerIcon },
        ]

        return {
            nodes,
            navigation,
            expandedKeys,
            selectedKey,
            sidebarOpen: ref(false),
        }
    },
    methods: {
        expandNode(node) {
            if (node.children && node.children.length) {
                this.expandedKeys[node.key] = true;

                for (let child of node.children) {
                    this.expandNode(child);
                }
            }
        },

        expandAll() {
            for (let node of this.nodes) {
                this.expandNode(node);
            }

            this.expandedKeys = { ...this.expandedKeys };
        },

        collapseAll() {
            this.expandedKeys = {};
        },

        async getCourseMaterial() {
            const res = await fastApi.get('/topics/materials')
            this.nodes = translateToTreeLibrary(res.data)
        },

        async generateFromNode(node) {
            alert('Course generation started')

            const payload = {
                'jobType': 'GenerateOutlineMaterial',
                ...node.data
            }
            
            const res = await fastApi.post('/jobs/generate', payload)
            if (res.status === 201) {
                alert('Generation Job Started')
            }
        },
    },
    computed: {
        outlineGenerated() {
            this.nodes && this.nodes?.length > 0
        }
    },

    mounted() {
        this.getCourseMaterial()
    }
}
</script>