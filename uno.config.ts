import {
  defineConfig,
  presetUno,
  presetAttributify,
  presetIcons
} from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      extraProperties: {
        'display': 'inline-block',
        'vertical-align': 'middle',
      },
    }),
  ],
  preflights: [
    {
      getCSS: () => `
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        a {
          text-decoration: none;
          color: inherit;
        }
        ul, ol {
          list-style: none;
        }
        body {
          overflow-x: hidden;
          width: 100%;
        }
      `,
    },
  ],
  theme: {
    fontFamily: {
      lobster: 'Lobster, cursive',
    },
    colors: {
      primary: {
        DEFAULT: '#7c3aed', // بنفش اصلی
        hover: '#6d28d9',
        light: '#ede9fe',   // بنفش خیلی روشن برای بک‌گراندها
        glow: 'rgba(124, 58, 237, 0.3)',
      },
      slate: {
        900: '#0f172a',
        400: '#94a3b8',
        100: '#f1f5f9',
        50: '#f8fafc',
      },
      success: '#22c55e',
    },
    borderRadius: {
      'custom-lg': '2.5rem',
      'custom-md': '1.8rem',
    }
  },
  shortcuts: {
    'app-card': 'bg-white rd-custom-lg shadow-2xl border border-slate-100 overflow-hidden',
    'btn-primary': 'py-4 px-8 bg-slate-900 text-white font-black text-xs uppercase tracking-[0.2em] rd-2xl transition-all duration-300 transform active:scale-95 hover:(bg-primary shadow-xl shadow-primary/30) border-none',
    'btn-secondary': 'py-4 px-8 bg-slate-100 text-slate-500 font-black text-xs uppercase tracking-[0.2em] rd-2xl transition-all duration-300 hover:(bg-slate-200 text-slate-800) border-none',
    'input-main': 'w-full bg-slate-100 border-none rd-2xl py-4 px-6 text-slate-700 font-medium focus:ring-2 focus:ring-primary focus:bg-white transition-all outline-none',
    // header
    'chat-avatar': 'w-14 h-14 rd-2xl object-cover shadow-sm',
    'status-pulse': 'w-2 h-2 bg-success rd-full animate-pulse',
    'nav-link': 'font-lobster p-3 mx-2 rounded-xl text-lg font-bold text-white hover:bg-white/10 transition-colors duration-200',
    'dropdown-card': 'absolute right-0 bg-slate-900 text-white shadow-xl rd-lg w-48 p-2 z-20 border border-white/10',
    'badge-ping': 'absolute -top-1 -right-1 flex h-4 w-4',
    // post
    'post-card': 'bg-white rd-2xl my-5 pb-4 shadow-[0_10px_40px_-10px_rgba(0,0,0,0.1)] border border-slate-100 overflow-hidden transition-all duration-400 hover:shadow-[0_20px_50px_-12px_rgba(124,58,237,0.15)] hover:-translate-y-1.5',
    'post-img-container': 'h-64 w-full overflow-hidden',
    'tag-item': 'bg-slate-100/80 backdrop-blur-md text-slate-600 rd-xl px-4 py-1.5 text-xs font-semibold hover:bg-primary hover:text-white transition-all',
    'avatar-ring': 'w-10 h-10 rd-full object-cover ring-2 ring-slate-50 border-2 border-white shadow-sm',
    'post-title': 'font-lobster text-start leading-5 mr-1',
    'post-text-main': 'font-lobster text-4xl mb-6 px-4 text-slate-800 leading-tight',
    'link-muted': 'text-slate-400 text-sm hover:text-primary transition-colors hover:underline',
    'input-form': 'w-full px-4 py-3 bg-slate-50 border-1 border-transparent rd-2xl focus:(bg-white border-primary ring-4 ring-primary/10) outline-none transition-all duration-300 text-slate-700 font-medium',
    'tag-btn': 'px-4 py-2 rd-full border-1 text-xs font-bold uppercase tracking-wider transition-all duration-200 shadow-sm',
    // hero
    'btn-hero': 'inline-block bg-primary text-white px-8 py-3 rd-full font-bold transition-all duration-300 hover:(bg-white text-primary scale-105) shadow-lg',
    'hero-overlay': 'absolute inset-0 bg-slate-900/60 z--1',
    // sidebar
    'sidebar-item': 'flex items-center p-2 rd-xl transition-all duration-200 hover:bg-slate-100 group',
    'sidebar-active': 'bg-primary/10 text-primary border-r-4 border-primary rd-r-none',
    'sidebar-card': 'bg-white rd-2xl shadow-sm border border-slate-100 p-4 mb-4',
    //
    'comment-input-container': 'flex items-center gap-2 bg-slate-50 p-2 rd-2xl border border-slate-100 focus-within:(border-primary bg-white shadow-sm) transition-all duration-300',
    // tabs
    'tab-btn': 'px-4 py-2 rd-xl text-sm font-bold text-slate-500 transition-all hover:(bg-slate-100 text-slate-800) cursor-pointer',
    'tab-selected': '!bg-primary !text-white shadow-md shadow-primary/20',
    'comment-card': 'w-full bg-white rd-2xl p-5 shadow-sm border border-slate-100 mb-4 block',
    'btn-action': 'flex items-center gap-1.5 px-3 py-1.5 rd-lg transition-all text-sm font-medium',
    'badge-primary': 'bg-primary/10 text-primary px-2 py-0.5 rd-full text-[11px] font-bold',
    // ptofile
    'profile-card': '!bg-white rd-[2.5rem] p-8 shadow-sm border border-slate-100 mb-6',
    'edit-btn': 'p-3 !bg-white/90 backdrop-blur-sm border border-slate-100 rd-2xl text-slate-400 hover:(text-primary shadow-lg bg-white) transition-all duration-300',
    'profile-stat': 'flex flex-col items-center px-6 py-2 border-r border-slate-100 last:border-0',
    // profile
    'admin-card': 'bg-white rd-[2rem] p-5 border border-slate-100 shadow-sm flex items-center justify-between group hover:(shadow-xl shadow-slate-200/50 -translate-y-1) transition-all duration-300',
    'tab-pill': 'px-6 py-2.5 rd-xl transition-all font-black text-xs uppercase tracking-widest flex items-center gap-2',
  },
  content: {
    pipeline: {
      include: [
        'templates/*.html',
        'templates/**/*.html',
        'templates/**/**/*.html',
      ],
    },
  },
})