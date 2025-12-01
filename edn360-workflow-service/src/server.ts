import express from 'express';
import dotenv from 'dotenv';
import { runWorkflow } from './edn360_workflow';

dotenv.config();

const app = express();
app.use(express.json({ limit: '10mb' }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'edn360-workflow-service' });
});

// Endpoint principal: ejecutar workflow EDN360
app.post('/api/edn360/run-training-workflow', async (req, res) => {
  try {
    console.log('🚀 Ejecutando workflow EDN360...');
    console.log(`📦 Input size: ${JSON.stringify(req.body).length} chars`);
    
    // EDN360Input completo (user_profile + questionnaires + context)
    const edn360Input = req.body;
    
    // Convertir a string para pasarlo al workflow
    const inputJsonStr = JSON.stringify(edn360Input);
    
    // Ejecutar workflow
    const result = await runWorkflow({ input_as_text: inputJsonStr });
    
    console.log('✅ Workflow ejecutado correctamente');
    console.log(`📤 Output size: ${JSON.stringify(result).length} chars`);
    
    // Verificar que el resultado tenga la estructura esperada
    if (!result || typeof result !== 'object') {
      throw new Error('El workflow no devolvió un objeto válido');
    }
    
    if (!result.client_training_program_enriched) {
      console.error('❌ Respuesta sin client_training_program_enriched:', result);
      throw new Error('La respuesta no contiene client_training_program_enriched');
    }
    
    // Devolver el resultado completo
    return res.json(result);
    
  } catch (err: any) {
    console.error('❌ Error ejecutando workflow EDN360:', err);
    
    return res.status(500).json({
      error: 'Error ejecutando workflow EDN360',
      message: err?.message ?? String(err),
      details: err?.stack
    });
  }
});

const PORT = process.env.EDN360_WORKFLOW_PORT || 4000;

app.listen(PORT, () => {
  console.log(`✅ EDN360 Workflow Service corriendo en puerto ${PORT}`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`   Endpoint: http://localhost:${PORT}/api/edn360/run-training-workflow`);
});
