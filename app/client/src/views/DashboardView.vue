
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
                                                    <a :href="item.href" :class="[item.current ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800', 'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']">
                                                        <component :is="item.icon" class="h-6 w-6 shrink-0" aria-hidden="true" />
                                                        {{ item.name }}
                                                    </a>
                                                </li>
                                            </ul>
                                        </li>
                                        <li>
                                            <div class="text-xs font-semibold leading-6 text-gray-400">Commands</div>
                                            <ul role="list" class="-mx-2 mt-2 space-y-1">
                                                <!-- <li v-for="command in commands" :key="command.name">
                                                    <button :click="command.method()" type="button" class="rounded-md bg-white/10 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-white/20">{{ command.name }}</button>
                                                </li> -->
                                            </ul>
                                        </li>
                                        <li class="-mx-6 mt-auto">
                                            <a href="#" class="flex items-center gap-x-4 px-6 py-3 text-sm font-semibold leading-6 text-white hover:bg-gray-800">
                                                <img class="h-8 w-8 rounded-full bg-gray-800" :src="profileImg" alt="" />
                                                <span class="sr-only">Your profile</span>
                                                <span aria-hidden="true">George Bush</span>
                                            </a>
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
                                    <a :href="item.href" :class="[item.current ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800', 'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']">
                                        <component :is="item.icon" class="h-6 w-6 shrink-0" aria-hidden="true" />
                                        {{ item.name }}
                                    </a>
                                </li>
                            </ul>
                        </li>
                        <li>
                            <div class="text-xs font-semibold leading-6 text-gray-400">Commands</div>
                            <ul role="list" class="-mx-2 mt-2 space-y-1">
                                <!-- <li v-for="command in commands" :key="command.name">
                                    <button :click="command.method" type="button" class="rounded-md bg-white/10 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-white/20">{{ command.name }}</button>
                                </li> -->
                            </ul>
                        </li>
                        <li class="-mx-6 mt-auto">
                            <a href="#" class="flex items-center gap-x-4 px-6 py-3 text-sm font-semibold leading-6 text-white hover:bg-gray-800">
                                <img class="h-8 w-8 rounded-full bg-gray-800" :src="profileImg" alt="" />
                                <span class="sr-only">Your profile</span>
                                <span aria-hidden="true">George Bush</span>
                            </a>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>

        <div class="xl:pl-72">
            <main class="lg:pr-96">
                <header class="flex items-center justify-between border-b border-white/5 px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
                    <h1 class="text-base font-semibold leading-7 text-white">Course Material</h1>
                </header>

                <!-- Content -->
                <div class="p-8">
                    <div v-if="nodes?.length">
                        <div class="flex flex-wrap gap-2 mb-4">
                            <button type="button" class="rounded-md bg-white/10 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-white/20" label="Expand All" @click="expandAll">Expand All</button>
                            <button type="button" class="rounded-md bg-white/10 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-white/20" label="Collapse All" @click="collapseAll">Collapse All</button>
                        </div>
                    </div>

                    <div v-if="nodes?.length">
                        <div class="p-4 flex justify-center">
                            <Tree v-model:expandedKeys="expandedKeys" class="w-full" :value="nodes">
                                <template #default="slotProps">
                                    <p class="p-1">{{ slotProps.node.label }}</p>
                                </template>
                                <template #url="slotProps">
                                    <div class="flex">
                                        <a class="p-1 text-blue-500" :href="slotProps.node?.data?.url ?? '#'">
                                            {{ slotProps.node.label }}
                                        </a>
                                        <span class="p-2.5 items-center">
                                            <div :class="[slotProps.node?.data?.exists ? 'text-green-400 bg-green-400/10' : 'text-rose-400 bg-rose-400/10', 'flex-none rounded-full p-1']">
                                                <div class="h-1.5 w-1.5 rounded-full bg-current"></div>
                                            </div>
                                        </span>
                                    </div>
                                </template>
                            </Tree>
                        </div>
                    </div>
                    <div v-else>
                        No Courses Generated Yet
                    </div>
                </div>
            </main>
        </div>
    </div>
</template>
  
<script lang="ts">
import { ref } from 'vue'
import flaskApi from '@/router/api'
import Tree from 'primevue/tree';
import 'primeicons/primeicons.css'
import {
    Dialog,
    DialogPanel,
    TransitionChild,
    TransitionRoot,
} from '@headlessui/vue'
import {
    ServerIcon,
    XMarkIcon,
    FolderIcon,
} from '@heroicons/vue/24/outline'

export default {
    name: 'DashboardView',
    components: {
        Tree,
        Dialog,
        DialogPanel,
        TransitionChild,
        TransitionRoot,
        ServerIcon,
        XMarkIcon,
        FolderIcon,
    },
    data() {
        const profileImg = 'data:image/jpeg;base64,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'
        const nodes: any = ref([]);
        const expandedKeys: any = ref({});
        const selectedKey = ref(undefined);
        const navigation = [
            { name: 'Logs', href: '#', icon: ServerIcon, current: true },
        ]
        const commands = [
            { id: 1, name: 'Run Course Generator', method: this.runCourseGenerator },
        ]

        return {
            profileImg,
            nodes,
            navigation,
            commands,
            expandedKeys,
            selectedKey,
            sidebarOpen: ref(false),
        }
    },
    methods: {
        translateToTreeLibrary(data: any) {
            if (!data || data?.length === 0) {
                return []
            }

            return data.map((topic: any) => {
                const topicChildren = topic.children.map((course: any) => {
                    const courseChildren = course.children.map((chapter: any) => {
                        const chapterChildren = chapter.children.map((page: any) => {
                            return {
                                name: page.slug,
                                key: `lesson-${page.id}`,
                                label: `Page: ${page.name}`,
                                icon: 'pi pi-fw pi-file',
                                data: {
                                    exists: page?.generated ?? false,
                                    url: `/page/${page.id}`
                                },
                                type: 'url'
                            }
                        })
                        return {
                            name: chapter.slug,
                            key: `lesson-${chapter.id}`,
                            label: chapter.name,
                            icon: 'pi pi-fw pi-file',
                            children: chapterChildren
                        }
                    })
                    return {
                        name: course.slug,
                        key: `course-${course.id}`,
                        label: course.name,
                        icon: 'pi pi-fw pi-book',
                        children: courseChildren
                    }
                })
                return {
                    name: topic.slug,
                    key: `topic-${topic.id}`,
                    label: topic.name,
                    icon: 'pi pi-fw pi-hashtag',
                    children: topicChildren
                }
            })
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
        expandNode(node: any) {
            if (node.children && node.children.length) {
                this.expandedKeys[node.key] = true;

                for (let child of node.children) {
                    this.expandNode(child);
                }
            }
        },

        async runCourseGenerator() {
            await flaskApi.post('/generate-courses', {})
            alert("Course Creator started!")
        },

        async getCourseMaterial() {
            return await flaskApi.get('/course-material')
        },

        startPolling() {
            setInterval(this.getCourseMaterial, 5000);
        }
    },
    async mounted() {
        const material = await this.getCourseMaterial()
        this.nodes = this.translateToTreeLibrary(material)
    }
}
</script>