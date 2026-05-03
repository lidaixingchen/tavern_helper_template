# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

本项目是酒馆助手 (Tavern Helper) 的前端界面或脚本编写模板。产物运行在 SillyTavern (酒馆) 的无沙盒 iframe 中，直接调用酒馆助手提供的接口与酒馆交互。

## 常用命令

```bash
pnpm build          # 生产模式打包 src/ 和 示例/ 中的项目到 dist/
pnpm build:dev      # 开发模式打包
pnpm watch          # 开发模式监听 + 热重载 (通过 socket.io 推送到酒馆网页)
pnpm lint           # ESLint 检查
pnpm lint:fix       # ESLint 自动修复
pnpm format         # Prettier 格式化
pnpm dump           # 将 schema.ts 转换为 schema.json
pnpm sync           # 打包酒馆同步文件 (角色卡/世界书/预设)
```

打包入口: webpack 会扫描 `{示例,src}/**/index.{ts,tsx,js,jsx}` 自动发现所有项目。

## 架构

### 项目类型判定

每个子文件夹是一个独立项目，由文件夹内容决定类型:

- 含 `index.ts` + `index.html` → **前端界面** (iframe 前台显示)
- 仅含 `index.ts` → **脚本** (iframe 后台运行)

### 关键目录

- `src/` — 用户项目代码
- `示例/` — 示例项目 (不要删除，AI 需参考)
- `util/` — 公共工具函数 (`common.ts`, `script.ts`, `mvu.ts`, `streaming.ts`)
- `@types/` — 酒馆助手接口类型定义 (全局可用，无需导入)
- `初始模板/` — 新建项目时的模板

### 路径别名

tsconfig 和 webpack 配置了:

- `@util/*` → `./util/*`
- `@/*` → `./src/*`

### 自动导入 (unplugin-auto-import)

以下模块在代码中可直接使用，无需 import: `vue`, `pinia`, `@vueuse/core`, `dedent`, `klona`, `vue-final-modal`(useModal), `zod`(z)

### 外部化依赖

webpack 将部分库外部化为全局变量，打包时不会包含它们: `$`(jquery), `_`(lodash), `toastr`, `YAML`, `z`(zod), `Vue`, `VueRouter`。其他未显式外部化的依赖通过 CDN `module-import` 方式引入。

### 特殊导入语法

```ts
import content from './file?raw'    // 文件内容作为字符串 (ts/scss 会先经 webpack 打包)
import html from './file.html'      // html-loader 最小化后作为字符串
import md from './file.md'          // remark-loader 解析为 HTML 字符串
import comp from './file.vue'       // Vue SFC
import style from './index.scss'    // 前端界面: 打包到 <head>; 脚本: style-loader 注入
```

### 热重载

`pnpm watch` 启动 socket.io 服务 (端口 6621)，编译完成后推送更新事件到酒馆网页。需确保酒馆网页中 `酒馆助手-实时监听-允许监听` 开关已启用。

## 编码规范

### 核心规则

- 使用 TypeScript，严格模式
- 运行环境是浏览器 iframe，**不能使用 Node.js 库**
- 优先使用酒馆助手接口 (`@types/` 中定义) 而非酒馆原生接口 (`@types/iframe/exported.sillytavern.d.ts`)
- 优先使用 Vue 3 (含 pinia/vue-router) 编写界面，而非 jQuery/DOM 操作
- 优先使用 Tailwind CSS + `<style scoped>` 设计样式

### 加载/卸载时机

```ts
// 加载: 用 jQuery，禁止 DOMContentLoaded
$(() => { /* 初始化 */ });

// 卸载: 用 pagehide，禁止 unload
$(window).on('pagehide', () => { /* 清理 */ });
```

`DOMContentLoaded` 不会在 `$('body').load(url)` 动态加载时触发，因此禁用。

### Vue + 酒馆变量模式

```ts
const Settings = z.object({ /* ... */ }).prefault({});
const settings = ref(Settings.parse(getVariables({ type: 'script', script_id: getScriptId() })));
watchEffect(() => replaceVariables(klona(settings.value), { type: 'script', script_id: getScriptId() }));
```

用 `klona()` 去除 Vue proxy 层后再写入酒馆。

### iframe 适配

- 禁用 `vh` 等受宿主高度影响的单位，用 `width` + `aspect-ratio`
- 避免 `min-height`、`overflow: auto` 等撑高父容器的属性
- 页面适配容器宽度，不产生横向滚动条

### 脚本中的 jQuery 作用域

脚本中的 `$` 通过 `window.$ = window.parent.$` 获取，直接作用于整个酒馆页面而非脚本 iframe。

### 脚本挂载 Vue 组件到酒馆页面

- 需要酒馆网页样式: 用 `createScriptIdDiv()` + `teleportStyle()` (禁止 tailwindcss 避免类名冲突)
- 独立样式隔离: 用 `createScriptIdIframe()` + `teleportStyle(iframe.contentDocument.head)`

### MVU 角色卡

变量存储在消息楼层变量的 `stat_data` 字段中。访问前需:

```ts
await waitGlobalInitialized('Mvu');
const data = Schema.parse(_.get(Mvu.getMvuData({ type: 'message', message_id }), 'stat_data'));
```

推荐用 `defineMvuDataStore` (pinia) 实现前端界面的双向同步。

### 错误处理

- 关键节点用 `console.info` 记录日志
- 可恢复错误: `console.warn` / `console.error`
- 致命错误: `throw Error`，顶部函数用 `errorCatched` 包裹

### 代码混淆

在 `index.ts` 顶部添加 `@obfuscate` 注释即可启用 webpack-obfuscator。
