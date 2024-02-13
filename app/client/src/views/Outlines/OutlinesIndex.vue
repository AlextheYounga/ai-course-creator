
<template>
    <div class="container mx-auto">
        <main>
            <div class="py-4">
                <Breadcrumbs />
            </div>

            <header class="flex items-center justify-between border-b border-white/5 px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
                <h1 class="text-base font-semibold leading-7 text-white">Outlines</h1>
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
                    <div class="h-72 p-4 flex justify-center">
                        <Tree v-model:expandedKeys="expandedKeys" class="w-full" :value="nodes">
                            <!-- Default Nodes -->
                            <template #default="slotProps">
                                <div class="flex items-center overflow-y-visible">
                                    <component :is="slotProps.node?.data?.icon" class="h-6 w-6 shrink-0 pl-1" aria-hidden="true" />
                                    <p class="p-1">{{ slotProps.node.label }}</p>
                                </div>
                            </template>

                            <!-- Outline Nodes -->
                            <template #outline="slotProps">
                                <div class="flex items-center overflow-y-visible">
                                    <component :is="slotProps.node?.data?.icon" class="h-6 w-6 shrink-0 pl-1" aria-hidden="true" />
                                    <p class="p-1">{{ slotProps.node.label }}</p>
                                    <Menu as="div" class="relative ml-auto">
                                        <MenuButton class="-m-2.5 block p-2.5 text-gray-400 hover:text-gray-500">
                                            <span class="sr-only">Open options</span>
                                            <EllipsisHorizontalIcon class="h-5 w-5" aria-hidden="true" />
                                        </MenuButton>
                                        <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100" leave-active-class="transition ease-in duration-75"
                                            leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
                                            <MenuItems class="absolute z-50 mt-0.5 bg-white origin-top-right rounded-md py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
                                                <MenuItem v-slot="{ active }">
                                                <button @click="copyOutline(slotProps.node)" :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-xs leading-6 text-gray-900 text-nowrap']">
                                                    Copy Outline
                                                </button>
                                                </MenuItem>
                                                <MenuItem v-slot="{ active }">
                                                <button @click="setMasterOutline(slotProps.node)" :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-xs leading-6 text-gray-900 text-nowrap']">
                                                    Set as Master Outline
                                                </button>
                                                </MenuItem>
                                                <MenuItem v-slot="{ active }">
                                                <router-link :to="`/outlines/${slotProps.node.data.id}`" :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-xs leading-6 text-gray-900 text-nowrap']">
                                                    Edit
                                                </router-link>
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
                    No Outlines Generated Yet
                </div>
            </div>
        </main>
    </div>
</template>
  
<script>
import { ref } from 'vue'
import flaskApi from '@/router/api'
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
    XMarkIcon,
    FolderIcon,
    AcademicCapIcon,
    DocumentTextIcon,
    BookOpenIcon,
    ListBulletIcon,
    LightBulbIcon,
} from '@heroicons/vue/24/outline';
import { EllipsisHorizontalIcon } from '@heroicons/vue/20/solid'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import YAML from 'yaml'

export default {
    name: 'OutlinesIndex',
    components: {
        Breadcrumbs,
        Tree,
        Dialog,
        DialogPanel,
        TransitionChild,
        TransitionRoot,
        Menu,
        MenuButton,
        MenuItem,
        MenuItems,
        XMarkIcon,
        FolderIcon,
        AcademicCapIcon,
        DocumentTextIcon,
        BookOpenIcon,
        LightBulbIcon,
        ListBulletIcon,
        EllipsisHorizontalIcon
    },
    data() {
        const nodes = ref([]);
        const expandedKeys = ref({});
        const selectedKey = ref(undefined);

        return {
            nodes,
            expandedKeys,
            selectedKey,
        }
    },
    methods: {
        // Tree methods
        translateToTreeLibrary(data) {
            if (!data || data?.length === 0) return []

            return data.map((topic) => {
                const topicChildren = topic.children.map((outline) => {
                    const outlineChildren = outline.children.map((course) => {
                        const courseChildren = course.children.map((chapter) => {
                            const chapterChildren = chapter.children.map((page) => {
                                return {
                                    name: page.slug,
                                    key: `lesson-${page.id}`,
                                    label: `Page: ${page.name}`,
                                    data: {
                                        topic_id: topic.id,
                                        id: page.id,
                                        entityType: 'Page',
                                        icon: DocumentTextIcon,
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
                                children: chapterChildren,
                                data: {
                                    topic_id: topic.id,
                                    id: chapter.id,
                                    entityType: 'Chapter',
                                    icon: BookOpenIcon,
                                },
                            }
                        })
                        return {
                            name: course.slug,
                            key: `course-${course.id}`,
                            label: course.name,
                            children: courseChildren,
                            data: {
                                topic_id: topic.id,
                                id: course.id,
                                entityType: 'Course',
                                icon: AcademicCapIcon,
                            },
                        }
                    })

                    const outlineName = topic.master_outline_id == outline.id ? `${outline.name} (Master)` : outline.name

                    return {
                        name: outline.name,
                        key: `outline-${outline.id}`,
                        label: outlineName,
                        children: outlineChildren,
                        data: {
                            topic_id: topic.id,
                            id: outline.id,
                            entityType: 'Outline',
                            outlineData: outline.master_outline,
                            icon: ListBulletIcon,
                        },
                        type: 'outline'
                    }
                })
                return {
                    name: topic.slug,
                    key: `topic-${topic.id}`,
                    label: topic.name,
                    children: topicChildren,
                    data: {
                        id: topic.id,
                        entityType: 'Topic',
                        icon: LightBulbIcon
                    }
                }
            })
        },

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

        async copyOutline(node) {
            try {
                const outlineData = YAML.stringify(node.data.outlineData, { indent: 4 })
                await navigator.clipboard.writeText(outlineData);
                alert('Copied outline');
            } catch (e) {
                console.log(e)
                alert('Cannot copy');
            }
        },

        async setMasterOutline(node) {
            const outlineId = node.data.id
            await flaskApi.put(`/outlines/${outlineId}/set-master`)
            alert('Master Outline Set');

            return this.getAllOutlines()
        },

        async getAllOutlines() {
            const material = await flaskApi.get('/outlines')
            this.nodes = this.translateToTreeLibrary(material)
        },
    },

    mounted() {
        this.getAllOutlines()
    }
}
</script>