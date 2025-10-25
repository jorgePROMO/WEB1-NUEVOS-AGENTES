// Mock data for development

export const mockUsers = [
  {
    id: '1',
    username: 'maria_lopez',
    email: 'maria@example.com',
    name: 'María López',
    role: 'user',
    subscription: {
      status: 'active',
      plan: 'team',
      startDate: '2024-01-15',
      paymentStatus: 'verified'
    },
    forms: [
      {
        id: 'f1',
        title: 'Formulario inicial de diagnóstico',
        url: 'https://forms.gle/aU7vnASAAYoxHRZk6',
        completed: true,
        sentDate: '2024-01-16'
      }
    ],
    pdfs: [
      {
        id: 'p1',
        title: 'Plan de Entrenamiento - Semana 1-4',
        type: 'training',
        url: '/pdfs/training_plan.pdf',
        uploadDate: '2024-01-20'
      },
      {
        id: 'p2',
        title: 'Plan de Nutrición - Semana 1-4',
        type: 'nutrition',
        url: '/pdfs/nutrition_plan.pdf',
        uploadDate: '2024-01-20'
      }
    ],
    alerts: [
      {
        id: 'a1',
        title: 'Cuestionario de seguimiento mensual',
        message: 'Es momento de completar tu cuestionario de seguimiento del primer mes',
        type: 'form',
        link: 'https://forms.gle/example1',
        date: '2024-02-15',
        read: false
      }
    ],
    nextReview: '2024-02-20'
  },
  {
    id: '2',
    username: 'carlos_ruiz',
    email: 'carlos@example.com',
    name: 'Carlos Ruiz',
    role: 'user',
    subscription: {
      status: 'pending',
      plan: 'team',
      startDate: '2024-02-01',
      paymentStatus: 'pending'
    },
    forms: [],
    pdfs: [],
    alerts: [],
    nextReview: null
  }
];

export const mockAdmin = {
  id: 'admin1',
  username: 'jorge_calcerrada',
  email: 'jorge@jorgecalcerrada.com',
  name: 'Jorge Calcerrada',
  role: 'admin'
};

export const mockMessages = [
  {
    id: 'm1',
    userId: '1',
    senderId: '1',
    senderName: 'María López',
    message: 'Hola Jorge, tengo una duda sobre el ejercicio de sentadillas',
    timestamp: '2024-01-25T10:30:00',
    isAdmin: false
  },
  {
    id: 'm2',
    userId: '1',
    senderId: 'admin1',
    senderName: 'Jorge Calcerrada',
    message: 'Hola María, ¿qué duda tienes? Cuéntame',
    timestamp: '2024-01-25T11:15:00',
    isAdmin: true
  },
  {
    id: 'm3',
    userId: '1',
    senderId: '1',
    senderName: 'María López',
    message: '¿Cuánto debo bajar en la sentadilla? Me cuesta mantener el equilibrio',
    timestamp: '2024-01-25T11:20:00',
    isAdmin: false
  },
  {
    id: 'm4',
    userId: '1',
    senderId: 'admin1',
    senderName: 'Jorge Calcerrada',
    message: 'Baja hasta donde puedas mantener la técnica correcta. Es mejor una sentadilla menos profunda pero bien hecha. Intenta bajar hasta que tus muslos estén paralelos al suelo. Si necesitas apoyo, puedes usar una silla detrás.',
    timestamp: '2024-01-25T11:25:00',
    isAdmin: true
  }
];

// Mock function to simulate login
export const mockLogin = (email, password) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (email === 'jorge@jorgecalcerrada.com' && password === 'admin123') {
        resolve({ user: mockAdmin, token: 'mock-admin-token' });
      } else if (email === 'maria@example.com' && password === 'user123') {
        resolve({ user: mockUsers[0], token: 'mock-user-token' });
      } else {
        reject(new Error('Credenciales incorrectas'));
      }
    }, 1000);
  });
};

// Mock function to simulate registration
export const mockRegister = (username, email, password) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newUser = {
        id: Date.now().toString(),
        username,
        email,
        name: username,
        role: 'user',
        subscription: {
          status: 'pending',
          plan: 'team',
          startDate: new Date().toISOString(),
          paymentStatus: 'pending'
        },
        forms: [],
        pdfs: [],
        alerts: [],
        nextReview: null
      };
      resolve({ user: newUser, token: 'mock-new-user-token' });
    }, 1000);
  });
};