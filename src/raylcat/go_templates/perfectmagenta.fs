#version 330

in vec2 fragTexCoord;

uniform sampler2D texture0;

out vec4 finalColor;

void main()
{
    float alpha = texture(texture0, fragTexCoord).a;

    finalColor = vec4(1.0, 0.0, 1.0, alpha);
}
