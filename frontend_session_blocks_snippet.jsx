/* Este es el snippet correcto para reemplazar la sección de bloques en UserDashboard.jsx */
/* Desde línea ~1325 hasta ~1540 */

{expandedSessions[idx] && (
  <CardContent className="space-y-4 pt-0">
    {/* Session Notes */}
    {session.session_notes && session.session_notes.length > 0 && (
      <div className="bg-red-50 border border-red-200 rounded-lg p-3">
        <p className="text-sm font-semibold text-red-800 mb-2">⚠️ Notas Importantes:</p>
        <ul className="space-y-1">
          {session.session_notes.map((note, i) => (
            <li key={i} className="text-sm text-red-700 flex items-start gap-2">
              <span>•</span>
              <span>{note}</span>
            </li>
          ))}
        </ul>
      </div>
    )}

    {/* NEW: 4-Block Structured View */}
    {session.bloques_estructurados ? (
      <div className="space-y-3">
        {/* Block A - Calentamiento */}
        {session.bloques_estructurados.A && (
          <Card className="border-2 border-orange-300 bg-orange-50/50">
            <CardHeader
              className="cursor-pointer hover:bg-orange-100/50 transition-colors py-3"
              onClick={() => toggleBlockExpand(idx, 'A')}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🔥</span>
                  <div>
                    <h5 className="font-bold text-gray-900 text-base">
                      Bloque A - Calentamiento
                    </h5>
                    <p className="text-xs text-gray-600">
                      {session.bloques_estructurados.A.duracion_minutos} min · {session.bloques_estructurados.A.nombre}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  {isBlockExpanded(idx, 'A') ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </Button>
              </div>
            </CardHeader>
            {isBlockExpanded(idx, 'A') && (
              <CardContent className="pt-0 space-y-2">
                {session.bloques_estructurados.A.ejercicios.map((ejercicio, eIdx) => (
                  <div key={eIdx} className="bg-white rounded-lg p-3 border border-orange-200">
                    <div className="flex items-start gap-2">
                      <span className="font-bold text-orange-600 min-w-[24px]">{ejercicio.orden}.</span>
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900 text-sm">{ejercicio.nombre}</p>
                        {ejercicio.duracion_minutos && (
                          <p className="text-xs text-gray-600 mt-1">Duración: {ejercicio.duracion_minutos} min</p>
                        )}
                        {(ejercicio.series || ejercicio.reps) && (
                          <p className="text-xs text-gray-600 mt-1">
                            {ejercicio.series && `${ejercicio.series} series`}
                            {ejercicio.series && ejercicio.reps && ' × '}
                            {ejercicio.reps && `${ejercicio.reps} reps`}
                          </p>
                        )}
                        {ejercicio.instrucciones && (
                          <p className="text-xs text-gray-500 mt-1 italic">{ejercicio.instrucciones}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            )}
          </Card>
        )}

        {/* Block B - Fuerza (IA) - EXPANDED BY DEFAULT */}
        {session.bloques_estructurados.B && (
          <Card className="border-2 border-blue-400 bg-blue-50/50">
            <CardHeader
              className="cursor-pointer hover:bg-blue-100/50 transition-colors py-3"
              onClick={() => toggleBlockExpand(idx, 'B')}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">💪</span>
                  <div>
                    <h5 className="font-bold text-gray-900 text-base">
                      Bloque B - Fuerza Principal
                    </h5>
                    <p className="text-xs text-gray-600">
                      Entrenamiento generado por IA
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  {isBlockExpanded(idx, 'B') ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </Button>
              </div>
            </CardHeader>
            {isBlockExpanded(idx, 'B') && session.bloques_estructurados.B.bloques_fuerza && (
              <CardContent className="pt-0 space-y-3">
                {session.bloques_estructurados.B.bloques_fuerza.map((block, blockIdx) => (
                  <div key={blockIdx} className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-3 md:p-4">
                    <h6 className="font-bold text-gray-900 mb-3 text-sm">
                      {block.primary_muscles && block.primary_muscles.length > 0 ? block.primary_muscles.join(', ') : `Bloque ${blockIdx + 1}`}
                    </h6>
                    
                    {/* Desktop: Table Layout */}
                    <div className="hidden md:block">
                      <div className="grid grid-cols-[50px_1fr_80px_80px_60px] gap-3 items-center bg-gray-200 px-3 py-2 rounded mb-2">
                        <div className="text-xs font-semibold text-gray-700 text-center">#</div>
                        <div className="text-xs font-semibold text-gray-700">Ejercicio</div>
                        <div className="text-xs font-semibold text-gray-700 text-center">Series</div>
                        <div className="text-xs font-semibold text-gray-700 text-center">Reps</div>
                        <div className="text-xs font-semibold text-gray-700 text-center">RPE</div>
                      </div>

                      <div className="space-y-2">
                        {block.exercises && block.exercises.map((exercise, exIdx) => (
                          <div key={exIdx} className="bg-white rounded border border-gray-200 p-3">
                            <div className="grid grid-cols-[50px_1fr_80px_80px_60px] gap-3 items-center mb-2">
                              <div className="text-center text-sm font-bold text-blue-600">
                                {exercise.order}
                              </div>
                              <div className="text-sm font-semibold text-gray-900">
                                {exercise.name}
                              </div>
                              <div className="text-sm text-center font-medium text-gray-900">
                                {exercise.series}
                              </div>
                              <div className="text-sm text-center font-medium text-gray-900">
                                {exercise.reps}
                              </div>
                              <div className="text-sm text-center font-medium text-gray-900">
                                {exercise.rpe}
                              </div>
                            </div>
                            {exercise.notes && (
                              <p className="text-xs text-gray-600 mb-2 pl-2 italic">{exercise.notes}</p>
                            )}
                            {exercise.video_url && (
                              <Button
                                onClick={() => handleOpenVideoModal(exercise.video_url)}
                                size="sm"
                                variant="outline"
                                className="w-full text-xs border-blue-300 text-blue-700 hover:bg-blue-50"
                              >
                                <ExternalLink className="h-3 w-3 mr-1" />
                                Ver Video del Ejercicio
                              </Button>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Mobile: Card Layout */}
                    <div className="md:hidden space-y-3">
                      {block.exercises && block.exercises.map((exercise, exIdx) => (
                        <div key={exIdx} className="bg-white rounded-lg border-2 border-gray-300 p-4 shadow-sm">
                          {/* Número de ejercicio */}
                          <div className="flex items-start gap-3 mb-3">
                            <div className="flex-shrink-0 w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                              <span className="text-white font-bold text-lg">{exercise.order}</span>
                            </div>
                            <div className="flex-1">
                              <h6 className="font-bold text-gray-900 text-base leading-tight">
                                {exercise.name}
                              </h6>
                            </div>
                          </div>

                          {/* Info del ejercicio */}
                          <div className="grid grid-cols-3 gap-3 mb-3">
                            <div className="bg-blue-50 rounded-lg p-3 text-center">
                              <p className="text-xs text-gray-600 mb-1">Series</p>
                              <p className="font-bold text-xl text-blue-600">{exercise.series}</p>
                            </div>
                            <div className="bg-green-50 rounded-lg p-3 text-center">
                              <p className="text-xs text-gray-600 mb-1">Reps</p>
                              <p className="font-bold text-xl text-green-600">{exercise.reps}</p>
                            </div>
                            <div className="bg-orange-50 rounded-lg p-3 text-center">
                              <p className="text-xs text-gray-600 mb-1">RPE</p>
                              <p className="font-bold text-xl text-orange-600">{exercise.rpe}</p>
                            </div>
                          </div>

                          {/* Notas */}
                          {exercise.notes && (
                            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mb-3">
                              <p className="text-sm text-gray-700 italic">{exercise.notes}</p>
                            </div>
                          )}

                          {/* Botón de video */}
                          {exercise.video_url && (
                            <Button
                              onClick={() => handleOpenVideoModal(exercise.video_url)}
                              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3"
                            >
                              <ExternalLink className="h-4 w-4 mr-2" />
                              Ver Video del Ejercicio
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </CardContent>
            )}
          </Card>
        )}

        {/* Block C - Core/ABS */}
        {session.bloques_estructurados.C && (
          <Card className="border-2 border-purple-300 bg-purple-50/50">
            <CardHeader
              className="cursor-pointer hover:bg-purple-100/50 transition-colors py-3"
              onClick={() => toggleBlockExpand(idx, 'C')}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🧱</span>
                  <div>
                    <h5 className="font-bold text-gray-900 text-base">
                      Bloque C - Core / ABS
                    </h5>
                    <p className="text-xs text-gray-600">
                      {session.bloques_estructurados.C.duracion_minutos} min · {session.bloques_estructurados.C.nombre}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  {isBlockExpanded(idx, 'C') ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </Button>
              </div>
            </CardHeader>
            {isBlockExpanded(idx, 'C') && (
              <CardContent className="pt-0 space-y-2">
                {session.bloques_estructurados.C.ejercicios.map((ejercicio, eIdx) => (
                  <div key={eIdx} className="bg-white rounded-lg p-3 border border-purple-200">
                    <div className="flex items-start gap-2">
                      <span className="font-bold text-purple-600 min-w-[24px]">{ejercicio.orden}.</span>
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900 text-sm">{ejercicio.nombre}</p>
                        {(ejercicio.series || ejercicio.reps) && (
                          <p className="text-xs text-gray-600 mt-1">
                            {ejercicio.series && `${ejercicio.series} series`}
                            {ejercicio.series && ejercicio.reps && ' × '}
                            {ejercicio.reps && `${ejercicio.reps} reps`}
                          </p>
                        )}
                        {ejercicio.instrucciones && (
                          <p className="text-xs text-gray-500 mt-1 italic">{ejercicio.instrucciones}</p>
                        )}
                        {ejercicio.video_url && (
                          <Button
                            onClick={() => handleOpenVideoModal(ejercicio.video_url)}
                            size="sm"
                            variant="outline"
                            className="w-full mt-2 text-xs border-purple-300 text-purple-700 hover:bg-purple-50"
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            Ver Video
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            )}
          </Card>
        )}

        {/* Block D - Cardio */}
        {session.bloques_estructurados.D && (
          <Card className="border-2 border-green-300 bg-green-50/50">
            <CardHeader
              className="cursor-pointer hover:bg-green-100/50 transition-colors py-3"
              onClick={() => toggleBlockExpand(idx, 'D')}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🏃</span>
                  <div>
                    <h5 className="font-bold text-gray-900 text-base">
                      Bloque D - Cardio
                    </h5>
                    <p className="text-xs text-gray-600">
                      {session.bloques_estructurados.D.duracion_minutos} min · {session.bloques_estructurados.D.nombre}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  {isBlockExpanded(idx, 'D') ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </Button>
              </div>
            </CardHeader>
            {isBlockExpanded(idx, 'D') && (
              <CardContent className="pt-0">
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <div className="mb-3">
                    <h6 className="font-semibold text-gray-900 text-sm mb-2">Opción Recomendada:</h6>
                    <p className="text-sm text-gray-700">
                      {session.bloques_estructurados.D.opcion_seleccionada?.nombre || session.bloques_estructurados.D.opciones[0]?.nombre}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Duración: {session.bloques_estructurados.D.opcion_seleccionada?.duracion_minutos || session.bloques_estructurados.D.opciones[0]?.duracion_minutos} min
                    </p>
                    {(session.bloques_estructurados.D.opcion_seleccionada?.instrucciones || session.bloques_estructurados.D.opciones[0]?.instrucciones) && (
                      <p className="text-xs text-gray-500 mt-2 italic">
                        {session.bloques_estructurados.D.opcion_seleccionada?.instrucciones || session.bloques_estructurados.D.opciones[0]?.instrucciones}
                      </p>
                    )}
                  </div>
                  
                  {session.bloques_estructurados.D.opciones.length > 1 && (
                    <div className="mt-3 pt-3 border-t border-green-200">
                      <h6 className="font-semibold text-gray-700 text-xs mb-2">Otras opciones disponibles:</h6>
                      <ul className="space-y-1">
                        {session.bloques_estructurados.D.opciones.slice(1).map((opcion, oIdx) => (
                          <li key={oIdx} className="text-xs text-gray-600">
                            • {opcion.nombre} ({opcion.duracion_minutos} min)
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </CardContent>
            )}
          </Card>
        )}
      </div>
    ) : (
      /* LEGACY VIEW: Old block structure for backward compatibility */
      <div className="space-y-3">
        {session.blocks && session.blocks.map((block, blockIdx) => (
          <div key={blockIdx} className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-3 md:p-4">
            <h5 className="font-bold text-gray-900 mb-3 text-base">
              Bloque {block.id} - {block.primary_muscles ? block.primary_muscles.join(', ') : ''}
            </h5>
            
            {/* Desktop: Table Layout */}
            <div className="hidden md:block">
              <div className="grid grid-cols-[50px_1fr_80px_80px_60px] gap-3 items-center bg-gray-200 px-3 py-2 rounded mb-2">
                <div className="text-xs font-semibold text-gray-700 text-center">#</div>
                <div className="text-xs font-semibold text-gray-700">Ejercicio</div>
                <div className="text-xs font-semibold text-gray-700 text-center">Series</div>
                <div className="text-xs font-semibold text-gray-700 text-center">Reps</div>
                <div className="text-xs font-semibold text-gray-700 text-center">RPE</div>
              </div>

              <div className="space-y-2">
                {block.exercises && block.exercises.map((exercise, exIdx) => (
                  <div key={exIdx} className="bg-white rounded border border-gray-200 p-3">
                    <div className="grid grid-cols-[50px_1fr_80px_80px_60px] gap-3 items-center mb-2">
                      <div className="text-center text-sm font-bold text-blue-600">
                        {exercise.order}
                      </div>
                      <div className="text-sm font-semibold text-gray-900">
                        {exercise.name}
                      </div>
                      <div className="text-sm text-center font-medium text-gray-900">
                        {exercise.series}
                      </div>
                      <div className="text-sm text-center font-medium text-gray-900">
                        {exercise.reps}
                      </div>
                      <div className="text-sm text-center font-medium text-gray-900">
                        {exercise.rpe}
                      </div>
                    </div>
                    {exercise.notes && (
                      <p className="text-xs text-gray-600 mb-2 pl-2 italic">{exercise.notes}</p>
                    )}
                    {exercise.video_url && (
                      <Button
                        onClick={() => handleOpenVideoModal(exercise.video_url)}
                        size="sm"
                        variant="outline"
                        className="w-full text-xs border-blue-300 text-blue-700 hover:bg-blue-50"
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        Ver Video del Ejercicio
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Mobile: Card Layout */}
            <div className="md:hidden space-y-3">
              {block.exercises && block.exercises.map((exercise, exIdx) => (
                <div key={exIdx} className="bg-white rounded-lg border-2 border-gray-300 p-4 shadow-sm">
                  {/* Número de ejercicio */}
                  <div className="flex items-start gap-3 mb-3">
                    <div className="flex-shrink-0 w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-lg">{exercise.order}</span>
                    </div>
                    <div className="flex-1">
                      <h6 className="font-bold text-gray-900 text-base leading-tight">
                        {exercise.name}
                      </h6>
                    </div>
                  </div>

                  {/* Info del ejercicio */}
                  <div className="grid grid-cols-3 gap-3 mb-3">
                    <div className="bg-blue-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-600 mb-1">Series</p>
                      <p className="font-bold text-xl text-blue-600">{exercise.series}</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-600 mb-1">Reps</p>
                      <p className="font-bold text-xl text-green-600">{exercise.reps}</p>
                    </div>
                    <div className="bg-orange-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-600 mb-1">RPE</p>
                      <p className="font-bold text-xl text-orange-600">{exercise.rpe}</p>
                    </div>
                  </div>

                  {/* Notas */}
                  {exercise.notes && (
                    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mb-3">
                      <p className="text-sm text-gray-700 italic">{exercise.notes}</p>
                    </div>
                  )}

                  {/* Botón de video */}
                  {exercise.video_url && (
                    <Button
                      onClick={() => handleOpenVideoModal(exercise.video_url)}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Ver Video del Ejercicio
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    )}
  </CardContent>
)}
