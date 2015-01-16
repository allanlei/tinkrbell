# ffmpeg -ss 3 -i input.mp4 -vf "select=gt(scene\,0.4)" -frames:v 5 -vsync vfr fps=fps=1/600 out%02d.jpg
# ffmpeg -ss 3 -i ~/Videos/b.mov -vf "select=gt(scene\,0.2)" -vsync vfr -f image2 out%02d.jpg
# ffmpeg -i ~/Videos/sintel_4k.mov -vf "select=gt(scene\,0.01)" -vf "select=gte(t\,15)" -vsync vfr -vframes 1 -f image2 -y poster.jpg
# ffmpeg -ss 3 -i ~/Videos/b.mmov -vf "select=gt(scene\,0.5)" -vsync vfr -frames:v 1 -f image2 -y poster.jpg
