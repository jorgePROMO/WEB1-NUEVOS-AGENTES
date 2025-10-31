# 🎨 Guía de Diseño - Jorge Calcerrada Trainer Platform

## Paleta de Colores Corporativos

### Colores Principales

```css
/* Azul Principal - Identidad de marca */
--primary-blue: #3B82F6;        /* rgb(59, 130, 246) */
--primary-blue-hover: #2563EB;  /* rgb(37, 99, 235) */
--primary-blue-light: #60A5FA;  /* rgb(96, 165, 250) */
--primary-blue-dark: #1E40AF;   /* rgb(30, 64, 175) */

/* Verde - Acciones positivas */
--success-green: #10B981;       /* rgb(16, 185, 129) */
--success-green-hover: #059669; /* rgb(5, 150, 105) */
--success-green-600: #16A34A;   /* rgb(22, 163, 74) */
--success-green-700: #15803D;   /* rgb(21, 128, 61) */

/* Rojo - Alertas y eliminaciones */
--danger-red: #EF4444;          /* rgb(239, 68, 68) */
--danger-red-hover: #DC2626;    /* rgb(220, 38, 38) */

/* Amarillo - Advertencias */
--warning-yellow: #F59E0B;      /* rgb(245, 158, 11) */
--warning-yellow-hover: #D97706;/* rgb(217, 119, 6) */

/* Naranja - Gradientes hero */
--orange-accent: #FB923C;       /* rgb(251, 146, 60) */
--orange-gradient: #F97316;     /* rgb(249, 115, 22) */
```

### Colores de Fondo

```css
/* Fondos principales */
--background-white: #FFFFFF;
--background-gray-50: #F9FAFB;  /* rgb(249, 250, 251) */
--background-gray-100: #F3F4F6; /* rgb(243, 244, 246) */
--background-gray-900: #111827; /* rgb(17, 24, 39) - Footer */

/* Fondos de gradiente */
--gradient-blue-purple: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-hero: linear-gradient(to right, #3B82F6, #F59E0B);
```

### Colores de Texto

```css
--text-primary: #111827;        /* rgb(17, 24, 39) - Títulos */
--text-secondary: #6B7280;      /* rgb(107, 114, 128) - Descripciones */
--text-muted: #9CA3AF;          /* rgb(156, 163, 175) - Textos secundarios */
--text-white: #FFFFFF;
```

### Estados de UI

```css
/* Badges y estados */
--status-active: #10B981;       /* Verde - Activo */
--status-pending: #F59E0B;      /* Amarillo - Pendiente */
--status-inactive: #EF4444;     /* Rojo - Inactivo */
--status-verified: #3B82F6;     /* Azul - Verificado */
```

---

## Tipografía

### Fuentes

```css
/* Sistema de fuentes */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
  'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
  sans-serif;

/* Para código */
font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
```

### Escalas de Tamaño

```css
/* Títulos principales */
.hero-title: 3rem (48px) - font-weight: 800
.section-title: 2.25rem (36px) - font-weight: 800
.card-title: 1.5rem (24px) - font-weight: 700

/* Textos */
.body-large: 1.125rem (18px) - font-weight: 400
.body-regular: 1rem (16px) - font-weight: 400
.body-small: 0.875rem (14px) - font-weight: 400
.caption: 0.75rem (12px) - font-weight: 400
```

---

## Componentes UI

### Botones

```css
/* Botón Primario (Azul) */
.btn-primary {
  background: #3B82F6;
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
}
.btn-primary:hover {
  background: #2563EB;
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
}

/* Botón Secundario (Verde) */
.btn-success {
  background: #10B981;
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  font-weight: 600;
}
.btn-success:hover {
  background: #059669;
}

/* Botón Peligro (Rojo) */
.btn-danger {
  background: #EF4444;
  color: white;
}
.btn-danger:hover {
  background: #DC2626;
}

/* Botón Outline */
.btn-outline {
  background: transparent;
  color: #3B82F6;
  border: 2px solid #3B82F6;
}
```

### Cards

```css
.card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}
```

### Badges

```css
/* Badge Activo */
.badge-active {
  background: #10B981;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Badge Pendiente */
.badge-pending {
  background: #F59E0B;
  color: white;
}

/* Badge Verificado */
.badge-verified {
  background: #3B82F6;
  color: white;
}
```

### Inputs y Forms

```css
.input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #E5E7EB;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input:focus {
  outline: none;
  border-color: #3B82F6;
  ring: 2px solid rgba(59, 130, 246, 0.2);
}
```

---

## Espaciado (Spacing)

```css
/* Sistema de espaciado (basado en 0.25rem = 4px) */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
```

---

## Sombras (Shadows)

```css
/* Sombras estándar */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1);
--shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.25);

/* Sombra en hover (azul) */
--shadow-primary-hover: 0 10px 25px rgba(59, 130, 246, 0.3);
```

---

## Border Radius

```css
--radius-sm: 0.25rem;   /* 4px */
--radius-md: 0.5rem;    /* 8px */
--radius-lg: 1rem;      /* 16px */
--radius-xl: 1.5rem;    /* 24px */
--radius-full: 9999px;  /* Círculo completo */
```

---

## Animaciones

```css
/* Fade in up */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Aplicación */
.animate-fade-in-up {
  animation: fade-in-up 1s ease-out;
}

/* Hover lift effect */
.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-lift:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}
```

---

## Responsive Breakpoints

```css
/* Mobile First Approach */

/* Small devices (móviles) */
@media (min-width: 640px) { /* sm */ }

/* Medium devices (tablets) */
@media (min-width: 768px) { /* md */ }

/* Large devices (laptops) */
@media (min-width: 1024px) { /* lg */ }

/* Extra large devices (desktops) */
@media (min-width: 1280px) { /* xl */ }

/* 2xl devices */
@media (min-width: 1536px) { /* 2xl */ }
```

---

## Iconografía

**Librería utilizada:** Lucide React

```bash
npm install lucide-react
```

**Iconos principales:**
- Users, UserPlus, Edit, Trash2 (gestión usuarios)
- Calendar, Bell, MessageSquare (comunicación)
- FileText, Upload, Download (documentos)
- Send, Mail (mensajería)
- CheckCircle, XCircle, Target (estados)
- LogOut (autenticación)

**Tamaños estándar:**
- Pequeño: 16px (w-4 h-4)
- Normal: 20px (w-5 h-5)
- Grande: 24px (w-6 h-6)
- Extra grande: 32px (w-8 h-8)

---

## Assets e Imágenes

### Logo
- **Ubicación:** `/app/frontend/public/ecj_icon.svg`
- **Uso:** Header, manifest PWA

### Imágenes de Landing Page
Las imágenes están embebidas directamente en los componentes.

---

## Componentes de Shadcn/UI

**Librería:** Shadcn UI (Tailwind CSS + Radix UI)

**Componentes utilizados:**
- Button
- Card (Card, CardHeader, CardTitle, CardContent)
- Input
- Label
- Textarea
- Tabs (Tabs, TabsList, TabsTrigger, TabsContent)
- Badge
- Dialog (Modal)
- Select
- Checkbox

**Configuración:**
Los componentes están en `/app/frontend/src/components/ui/`

---

## PWA (Progressive Web App)

### Manifest
```json
{
  "name": "Jorge Calcerrada Trainer",
  "short_name": "ECJ Trainer",
  "theme_color": "#3B82F6",
  "background_color": "#FFFFFF"
}
```

### Service Worker
Ubicación: `/app/frontend/public/service-worker.js`
Cachea assets para funcionamiento offline.

---

## Mejores Prácticas

### CSS
1. Usar clases de Tailwind CSS cuando sea posible
2. Mantener estilos custom en App.css
3. Nombrar clases con BEM para componentes custom

### Colores
1. SIEMPRE usar variables CSS para colores
2. Nunca hardcodear valores hex en componentes
3. Mantener consistencia con la paleta definida

### Accesibilidad
1. Siempre incluir atributos `aria-label` en botones de íconos
2. Usar contrastes de color adecuados (WCAG AA)
3. Asegurar que todos los inputs tengan labels

### Performance
1. Optimizar imágenes (formato WebP cuando sea posible)
2. Lazy loading para componentes pesados
3. Minimizar animaciones innecesarias

---

## Notas para el Desarrollador

- La aplicación usa **Tailwind CSS** como framework principal de estilos
- Los componentes de UI son de **Shadcn/UI** (Radix UI + Tailwind)
- El diseño es **mobile-first** y totalmente responsive
- La aplicación es una **PWA** instalable en móviles
- Todos los colores corporativos están documentados arriba
- Mantener la consistencia visual es crítico para la marca

---

**Contacto de Marca:**
- Nombre: Jorge Calcerrada
- Email: ecjtrainer@gmail.com
- Colores principales: Azul (#3B82F6) y Verde (#10B981)