<template>
    <p class="text-lg">{{ this.data.description }}</p>
    <div class="codepen" data-prefill data-height="400" data-theme-id="1" data-default-tab="html,result">
        <pre :data-lang="this.template.language">{{ this.template.code }}</pre>
        <pre :data-lang="this.styles.language">{{ this.styles.code }}</pre>
        <pre :data-lang="this.scripts.language">{{ this.scripts.code }}</pre>
    </div>
</template>
<script>
import { useScriptTag } from '@vueuse/core'

const { load } = useScriptTag(
  'https://static.codepen.io/assets/embed/ei.js',
  () => {},
  { manual: true },
)

export default {
    name: 'Codepen',
    props: {
        data: {
            type: Object,
            required: true,
        }
    },
    data() {
        const template = {
            language: this.data.content.template.language,
            code: this.data.content.template?.content
        }
        const styles = {
            language: this.data.content.styles.language,
            content: this.data.content.styles.content
        }
        const scripts = {
            language: this.data.content.scripts.language,
            content: this.data.content.scripts.content
        }
        return {
            template: template,
            styles: styles,
            scripts: scripts
        }
    },
    created() {
        load()
    }
};
</script>