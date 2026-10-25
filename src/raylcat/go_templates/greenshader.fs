#version 330

in vec2 fragTexCoord;
uniform sampler2D texture0;
out vec4 finalColor;

void main()
{
    vec4 pixel = texture(texture0, fragTexCoord);

    if (pixel.a > 0.0) {
        finalColor = vec4(0.0, 1.0, 0.0, 1.0);
    } else {
        discard;
    }
}
