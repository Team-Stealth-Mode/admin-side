const video = document.getElementById('video')

Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
  faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
  faceapi.nets.faceRecognitionNet.loadFromUri('/models'),
  faceapi.nets.faceExpressionNet.loadFromUri('/models')
]).then(startVideo)

function startVideo() {
  navigator.getUserMedia(
    { video: { width: 600, height: 400 } },
    stream => video.srcObject = stream,
    err => console.error(err)
  )
}

video.addEventListener('play', () => {
  const canvas = faceapi.createCanvasFromMedia(video)
  document.body.append(canvas)
  const displaySize = { width: video.width, height: video.height }
  faceapi.matchDimensions(canvas, displaySize)
  setInterval(async () => {
    const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceExpressions()

    //onsole.log(detections)
    //  const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceExpressions()
    //const detections=await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
    //console.log('Box: ', detections[0].detection.box);
    extractFaceFromBox(video, detections[ 0 ].detection.box)
    const resizedDetections = faceapi.resizeResults(detections, displaySize)
    console.log(resizedDetections)
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
    faceapi.draw.drawDetections(canvas, resizedDetections)
    faceapi.draw.drawFaceLandmarks(canvas, resizedDetections)
    faceapi.draw.drawFaceExpressions(canvas, resizedDetections)
    for (const key in resizedDetections[ 0 ].expressions) {
      if (resizedDetections[ 0 ].expressions[ key ] > 0.77) {
        console.log(`${key}: ${resizedDetections[ 0 ].expressions[ key ]}`);
      }
    }
    //  console.log('your expression'+resizedDetections[0].expressions.neutral)
    //  console.log(faceapi)
    //  console.log(faceapi.FACE_EXPRESSION_LABELS)
  }, 1000)
})

async function extractFaceFromBox(inputImage, box) {
  const regionsToExtract = [
    new faceapi.Rect(box.x, box.y, box.width, box.height)
  ]
  // console.log('x',box.x)
  // console.log('y',box.y)
  // console.log('width',box.width)
  // console.log('height',box.height)

  let faceImages = await faceapi.extractFaces(inputImage, regionsToExtract)

  console.log('length:', faceImages.length)
  if (faceImages.length > 1) {
    alert("multiple faces found")
  }
  // else
  // {
  //     faceImages.forEach(cnv =>{      
  //         outputImage.src = cnv.toDataURL();      
  //     })
  // }   
}    