
<template>
    <div class="container mx-auto">
        <main>
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
                            <!-- Nest Dropdowns -->
                            <template #default="slotProps">
                                <div class="flex items-center overflow-y-visible">
                                    <component :is="slotProps.node?.data?.icon" class="h-6 w-6 shrink-0 pl-1" aria-hidden="true" />
                                    <p class="p-1">{{ slotProps.node.label }}</p>
                                </div>
                            </template>
                            <!-- Page Links -->
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
                    No Courses Generated Yet
                </div>
            </div>
        </main>
    </div>
</template>
  
<script lang="ts">
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
    ServerIcon,
    XMarkIcon,
    FolderIcon,
    AcademicCapIcon,
    DocumentTextIcon,
    BookOpenIcon,
    LightBulbIcon,
} from '@heroicons/vue/24/outline';
import { EllipsisHorizontalIcon } from '@heroicons/vue/20/solid'
import type { Topic, Course, Chapter, Page } from '@/types/ModelTypes';

type TopicOutlineEntities = Topic & {
    children: CourseWithRelations[]
}

type CourseWithRelations = Course & {
    children: ChapterWithPages[]
}

type ChapterWithPages = Chapter & {
    children: Page[]
}

export default {
    name: 'OutlinesView',
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
        AcademicCapIcon,
        DocumentTextIcon,
        BookOpenIcon,
        LightBulbIcon,
        EllipsisHorizontalIcon
    },
    data() {
        const nodes: any = ref([]);
        const expandedKeys: any = ref({});
        const selectedKey = ref(undefined);

        return {
            nodes,
            expandedKeys,
            selectedKey,
        }
    },
    methods: {
        // Tree methods
        translateToTreeLibrary(data: TopicOutlineEntities[]) {
            if (!data || data?.length === 0) return []

            return data.map((topic: TopicOutlineEntities) => {
                const topicChildren = topic.children.map((course: CourseWithRelations) => {
                    const courseChildren = course.children.map((chapter: ChapterWithPages) => {
                        const chapterChildren = chapter.children.map((page: Page) => {
                            return {
                                name: page.slug,
                                key: `lesson-${page.id}`,
                                label: `Page: ${page.name}`,
                                data: {
                                    topic_id: topic.id,
                                    id: page.id,
                                    entity_type: 'Page',
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
                                entity_type: 'Chapter',
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
                            entity_type: 'Course',
                            icon: AcademicCapIcon,
                        },
                    }
                })
                return {
                    name: topic.slug,
                    key: `topic-${topic.id}`,
                    label: topic.name,
                    children: topicChildren,
                    data: {
                        id: topic.id,
                        entity_type: 'Topic',
                        icon: LightBulbIcon
                    }
                }
            })
        },

        expandNode(node: any) {
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
            const material = await flaskApi.get('/course-material') as TopicOutlineEntities[]
            this.nodes = this.translateToTreeLibrary(material)
        },
    },

    mounted() {
        this.getCourseMaterial()
    }
}
</script>