<template>
	<v-ace-editor v-model:value="content" :lang="language" theme="one_dark" style="height: 300px" />
</template>

<script>
import { defineComponent } from 'vue'
import { VAceEditor } from 'vue3-ace-editor';
import ace from 'ace-builds';
import modeList from 'ace-builds/src-noconflict/ext-modelist';
ace.config.set('basePath', '../../../node_modules/ace-builds/src-noconflict')

export default defineComponent({
	name: 'CodeEditor',
	components: {
		VAceEditor
	},
	props: {
		interactive: {
			type: Object,
			required: false,
		}
	},
	methods: {
		getLanguage() {
			const language = this.$props.interactive.data['language'] ?? 'txt';
			const mode = modeList.getModeForPath(`file.${language}`).mode;
			const aceId = mode.split('/').pop()
			return aceId
		}
	},
	data() {
		return {
			content: this.$props.interactive.data['content'] ?? '',
			language: this.getLanguage()
		}
	},
});
</script>