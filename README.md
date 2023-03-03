# Aplicación desarrollada en Flask por Unai Zubeldia y Jon Ortega

La aplicación exige que el usuario se registre. Su funcionalidad principal consiste en la transcripción de un fichero audio a texto, para lo cual emplea el modelo Whisper desarrollado por OpenAI.

Además, dispone de funcionalidades adicionales. Por ejemplo, en base al histórico de audios transcritos, muestra estadísticas que informan sobre la temática, las palabras más frecuentes o relevantes... empleadas en los audios transcritos por el usuario.

De hecho, tratándose generalmente de textos largos, se proporciona un botón que resumen de manera automática el contenido del audio transcrito, ofreciendo al usuario el contenido deseado de una forma corta y concisa.

La aplicación cuida el diseño y la experiencia de usuario, guiándole en todo momento a través de los distintos apartados de la web y con botones de vuelta a casa accesibles en todo momento, además de una correcta gestión de los errores mostrando al usuario dónde está el fallo que no le deja continuar.